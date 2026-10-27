"""Motor H-MEM de Meterless dentro de MIDAZ (HU-15): memoria de decisiones del dueño.

H-MEM se publica como especificacion (Meterless/Meterless, engines/hmem/AGENTS.md) con una
referencia en TypeScript y una suite de conformidad; no hay paquete Python. Esto es un port
en Python (stdlib) de la referencia `engines/hmem/reference` (commit 1742dec, Apache-2.0), con
los mismos contratos: `source` y `provenance` obligatorios, formula hibrida de recuperacion,
deltas de feedback, ledger append-only, conflictos con compuerta 0.70, sleep con guardrails y
dreaming con aprobacion humana. Los vectores de conformidad oficiales se copian en
`midas/hmem_vectors/vectors.json` y corren en `tests/test_hmem.py`.

Diferencias con la referencia (anotadas): el tokenizador quita tildes antes de filtrar
(espanol), y las entidades incluyen ids de producto `P\\d{3}`.
Persistencia: JSON en `MIDAZ_HMEM_PATH` (por defecto `out/hmem/memoria.json`, ignorado por git).
"""
from __future__ import annotations

import copy
import json
import math
import os
import re
import time
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DAY_MS = 24 * 60 * 60 * 1000
DEFAULTS = {"retrievalTopN": 5, "retrievalThreshold": 0.35, "consolidationDays": 7, "archiveMinDays": 30,
            "archiveMaxAccess": 2, "synthesisCosine": 0.82, "dreamClusterMinSize": 2, "dreamRelatedness": 0.35,
            "maxDreamProposalsPerType": 8, "conflictAutoResolveGate": 0.7, "entityCap": 10, "relatedCap": 5,
            "recencyDays": 14}
FEEDBACK_DELTAS = {"helpful": 0.05, "not_helpful": -0.03, "wrong": -0.20}
LAYER_WEIGHT = {"long_term": 1.0, "working": 0.8, "short_term": 0.6}
ORIGINS = {"manual", "chat", "sql_receipt", "owner_message", "user_correction", "dreaming", "sleep"}
DOMAIN_KEYWORDS = {
    "precios": ["precio", "subi", "baje", "subir", "bajar", "descuento", "price"],
    "inventario": ["costo", "stock", "proveedor", "traer", "inventario"],
    "finanzas": ["gasto", "alquiler", "planilla", "faltante", "alcanza"],
    "personal": ["prefiero", "prefer", "me", "gusta"],
}
OPPOSING = [(r"\balways\b|\bsiempre\b", r"\bnever\b|\bnunca\b"), (r"\benable[ds]?\b", r"\bdisable[ds]?\b"),
            (r"\bprefer[s]?\b", r"\bavoid[s]?|dislike[s]?\b"), (r"\bsubi\b", r"\bbaje\b"),
            (r"\bon\b", r"\boff\b"), (r"\byes\b|\bsi\b", r"\bno\b")]


def clamp01(x: float) -> float:
    return min(1.0, max(0.0, x))


def tokenize(text: str) -> list[str]:
    t = unicodedata.normalize("NFKD", text.lower()).encode("ascii", "ignore").decode()
    return [x for x in re.split(r"\s+", re.sub(r"[^a-z0-9\s]", " ", t)) if len(x) > 1]


def _fnv1a(s: str) -> int:
    h = 0x811C9DC5
    for ch in s:
        h ^= ord(ch)
        h = (h * 0x01000193) & 0xFFFFFFFF
    return h


def embed(text: str) -> list[float]:
    """Embedder deterministico de la referencia (FNV-1a, 64 dims). Cambiable por uno real."""
    v = [0.0] * 64
    for tok in tokenize(text):
        h = _fnv1a(tok)
        v[h % 64] += (1 if (h >> 8) % 2 == 0 else -1) * (1 + ((h >> 16) % 8) / 8)
    n = math.sqrt(sum(x * x for x in v))
    return v if n == 0 else [x / n for x in v]


def cosine(a, b) -> float:
    return sum(x * y for x, y in zip(a, b))


def jaccard(a, b) -> float:
    sa, sb = set(a), set(b)
    if not sa or not sb:
        return 0.0
    i = len(sa & sb)
    return i / (len(sa) + len(sb) - i)


class MemoryError_(ValueError):
    pass


def snapshot(m: dict) -> dict:
    return {k: copy.deepcopy(v) for k, v in m.items() if k != "embedding"}


class TrustLedger:
    def __init__(self, hm):
        self.hm, self.entries = hm, []

    def log(self, memory_id, action, actor, **kw):
        self.entries.append({"memoryId": memory_id, "action": action, "actor": actor,
                             "timestamp": self.hm.clock(), **kw})

    def history(self, memory_id):
        return [e for e in self.entries if e["memoryId"] == memory_id]


class Store:
    def __init__(self, hm):
        self.hm, self.records, self.seq = hm, {}, 0

    def extract_entities(self, text: str) -> list[str]:
        ents = re.findall(r"\bP\d{3}\b", text) + [t for t in re.findall(r"\b[A-Z][\w-]{2,}", text)]
        out = []
        for e in ents:
            e = e.lower()
            if e not in out:
                out.append(e)
        return out[:DEFAULTS["entityCap"]]

    def classify_domain(self, content, tags, mtype) -> str:
        for t in tags:
            if t.startswith("project:"):
                return t[len("project:"):]
        toks, best, bs = set(tokenize(content)), "general", 0
        for d, kws in DOMAIN_KEYWORDS.items():
            s = sum(k in toks for k in kws) + (1 if d == "personal" and mtype in ("personal", "preference") else 0)
            if s > bs:
                best, bs = d, s
        return best

    def add(self, content, source, provenance=None, type="general", layer="working", confidence=0.7,
            tags=None, supersedes=None, derivedFrom=None, chatId=None, domain=None):
        if not content or not str(content).strip():
            raise MemoryError_("H-MEM: recuerdo sin contenido")
        if not source or not str(source).strip():
            raise MemoryError_("H-MEM: recuerdo sin source (rechazado por construccion)")
        now = self.hm.clock()
        prov = provenance or {"origin": "manual", "learnedAt": now, "label": source}
        if self.hm.strict_provenance and (prov.get("origin") not in ORIGINS or not prov.get("label")):
            raise MemoryError_("H-MEM: provenance invalida (origin del enum + label obligatorios)")
        self.seq += 1
        tags = list(tags or [])
        rec = {"id": f"mem-{self.seq}", "content": content, "type": type, "layer": layer, "timestamp": now,
               "lastAccessed": now, "accessCount": 0, "tags": tags, "embedding": embed(content),
               "confidence": clamp01(confidence), "source": source, "provenance": prov, "chatId": chatId,
               "domain": domain or self.classify_domain(content, tags, type),
               "entities": self.extract_entities(content), "relatedTo": [], "supersedes": supersedes,
               "supersededBy": None, "derivedFrom": list(derivedFrom or [])}
        for o in self.records.values():
            if len(rec["relatedTo"]) < DEFAULTS["relatedCap"] and cosine(o["embedding"], rec["embedding"]) > 0.6:
                rec["relatedTo"].append(o["id"])
        if supersedes and supersedes in self.records:
            self.records[supersedes]["supersededBy"] = rec["id"]
        self.records[rec["id"]] = rec
        self.hm.ledger.log(rec["id"], "create", self.hm.actor, newState=snapshot(rec))
        self.hm.persist()
        return rec

    def get(self, mid):
        return self.records.get(mid)

    def all(self):
        return list(self.records.values())

    def delete(self, mid, reason):
        m = self.records.pop(mid, None)
        if m:
            self.hm.ledger.log(mid, "delete", self.hm.actor, previousState=snapshot(m), details={"reason": reason})
            self.hm.persist()


class Retrieval:
    def __init__(self, hm):
        self.hm = hm

    def score(self, m, q):
        qe, qt = embed(q), tokenize(q)[:8]
        st = self.hm.store
        raw = (0.35 * clamp01(cosine(qe, m["embedding"])) + 0.20 * jaccard(qt, tokenize(m["content"]))
               + 0.10 * jaccard(qt, [t.lower() for t in m["tags"]])
               + 0.10 * (1 if m["domain"] == st.classify_domain(q, [], "general") else 0)
               + 0.15 * jaccard(st.extract_entities(q), m["entities"]) + 0.05 * LAYER_WEIGHT[m["layer"]]
               + 0.05 * math.exp(-((self.hm.clock() - m["lastAccessed"]) / DAY_MS) / DEFAULTS["recencyDays"])
               - 0.20 * (1 if m["supersededBy"] else 0))
        return clamp01(raw) * m["confidence"]

    def query(self, q, topN=None, threshold=None, chatId=None):
        th = DEFAULTS["retrievalThreshold"] if threshold is None else threshold
        scored = []
        for m in self.hm.store.all():
            if chatId and m["chatId"] and m["chatId"] != chatId:
                continue
            s = self.score(m, q)
            if s >= th:
                scored.append({"memory": m, "relevance": s})
        scored.sort(key=lambda x: (-x["relevance"], x["memory"]["id"]))
        top = scored[: topN or DEFAULTS["retrievalTopN"]]
        for x in top:
            x["memory"]["lastAccessed"] = self.hm.clock()
            x["memory"]["accessCount"] += 1
            self.hm.ledger.log(x["memory"]["id"], "read", self.hm.actor, details={"relevance": round(x["relevance"], 4)})
        lines = [f"[{x['memory']['layer']}] {x['memory']['content']} (provenance: {x['memory']['provenance'].get('label')})"
                 for x in top]
        return {"memories": top, "context": "\n".join(lines),
                "trace": {"retrievalReason": f"hybrid score >= {th}", "strategy": "minimal",
                          "scores": {x["memory"]["id"]: round(x["relevance"], 4) for x in top}}}


class Conflicts:
    def __init__(self, hm):
        self.hm, self.items, self.seq = hm, [], 0

    def scan(self):
        found, allm = [], self.hm.store.all()
        for i in range(len(allm)):
            for j in range(i + 1, len(allm)):
                c = self._check(allm[i], allm[j])
                if c:
                    found.append(c)
                    self.items.append(c)
                    self.hm.ledger.log(c["memoryA"], "conflict_detected", self.hm.actor,
                                       details={"with": c["memoryB"], "reason": c["reason"]})
        return found

    def _check(self, a, b):
        if b["id"] in (a["supersedes"], a["supersededBy"]) or a["id"] in (b["supersedes"], b["supersededBy"]):
            return None
        sim, reason, conf = cosine(a["embedding"], b["embedding"]), "", 0.0
        for p, q in OPPOSING:
            if ((re.search(p, a["content"], re.I) and re.search(q, b["content"], re.I))
                    or (re.search(q, a["content"], re.I) and re.search(p, b["content"], re.I))) and sim > 0.5:
                reason, conf = "opposing phrase pair on similar content", 0.5 + 0.3 * sim
        if not reason and sim > 0.8:
            na, nb = re.findall(r"\d+(?:\.\d+)?", a["content"]), re.findall(r"\d+(?:\.\d+)?", b["content"])
            if na and nb and na != nb:
                reason, conf = "high-similarity conflicting numeric values", 0.55 + 0.25 * sim
        if not reason:
            return None
        if set(a["entities"]) & set(b["entities"]):
            conf += 0.1
        if a["domain"] == b["domain"]:
            conf += 0.05
        if b["id"] in a["relatedTo"]:
            conf -= 0.1
        self.seq += 1
        return {"id": f"conflict-{self.seq}", "memoryA": a["id"], "memoryB": b["id"], "reason": reason,
                "confidence": clamp01(conf), "resolved": False}

    def auto_resolve(self, c):
        st, now = self.hm.store, max(1, self.hm.clock())
        a, b = st.get(c["memoryA"]), st.get(c["memoryB"])

        def sc(m):
            return (0.3 * (m["lastAccessed"] / now) + 0.2 * min(1, m["accessCount"] / 10) + 0.25 * m["confidence"]
                    + 0.1 * min(1, len(m["content"]) / 200)
                    + 0.15 * (1 if m["provenance"].get("origin") == "user_correction" else 0.5))
        sa, sb = sc(a), sc(b)
        dc = clamp01(c["confidence"] * 0.6 + abs(sa - sb) / max(sa, sb) * 0.8)
        if dc < DEFAULTS["conflictAutoResolveGate"]:
            return "queued"
        win, lose = (a, b) if sa >= sb else (b, a)
        prev = snapshot(lose)
        lose["supersededBy"] = win["id"]  # se conserva y se penaliza; nunca se borra
        c["resolved"] = True
        self.hm.ledger.log(lose["id"], "conflict_resolved", self.hm.actor, previousState=prev,
                           newState=snapshot(lose), details={"winner": win["id"], "decisionConfidence": round(dc, 3)})
        self.hm.persist()
        return "resolved"


class Sleep:
    def __init__(self, hm):
        self.hm = hm

    def preview(self):
        now, allm = self.hm.clock(), self.hm.store.all()
        referenced = {d for m in allm for d in m["derivedFrom"]} | {r for m in allm for r in m["relatedTo"]}
        hubs = {m["id"] for m in allm if len(m["relatedTo"]) >= 3}
        to_archive = [m["id"] for m in allm
                      if now - m["timestamp"] >= DEFAULTS["archiveMinDays"] * DAY_MS
                      and m["accessCount"] <= DEFAULTS["archiveMaxAccess"] and m["layer"] != "long_term"
                      and not m["derivedFrom"] and m["source"] != "dreaming"
                      and m["id"] not in referenced and m["id"] not in hubs]
        to_promote = [m["id"] for m in allm if m["layer"] == "short_term"
                      and now - m["lastAccessed"] >= DEFAULTS["consolidationDays"] * DAY_MS]
        return {"toArchive": to_archive, "toConsolidate": to_promote}

    def execute(self, plan):
        backup_id = f"backup-{self.hm.clock()}"
        self.hm.backups[backup_id] = copy.deepcopy(self.hm.store.records)
        for mid in plan["toConsolidate"]:
            m = self.hm.store.get(mid)
            if m:
                m["layer"] = "working"
                self.hm.ledger.log(mid, "sleep_consolidate", self.hm.actor)
        for mid in plan["toArchive"]:
            self.hm.ledger.log(mid, "sleep_archive", self.hm.actor)
            self.hm.store.delete(mid, "sleep archive")
        return {"backupId": backup_id, "archived": len(plan["toArchive"])}


class Dreaming:
    def __init__(self, hm):
        self.hm, self.proposals, self.seq = hm, {}, 0

    def dream(self):
        allm, created, used = self.hm.store.all(), [], set()

        def rel(a, b):
            return (0.5 * max(0, cosine(a["embedding"], b["embedding"])) + 0.2 * jaccard(a["tags"], b["tags"])
                    + 0.1 * (a["domain"] == b["domain"]) + 0.2 * jaccard(a["entities"], b["entities"]))

        def propose(**p):
            self.seq += 1
            p.update(id=f"dream-{self.seq}", status="proposed")
            self.proposals[p["id"]] = p
            created.append(p)
            self.hm.ledger.log(p["id"], "dream_proposed", self.hm.actor, details={"type": p["type"]})
        for seed in allm:
            if seed["id"] in used:
                continue
            g = [seed] + [o for o in allm if o["id"] != seed["id"] and o["id"] not in used
                          and rel(seed, o) >= DEFAULTS["dreamRelatedness"]]
            if len(g) >= DEFAULTS["dreamClusterMinSize"]:
                used |= {m["id"] for m in g}
                propose(type="insight", content=" + ".join(m["content"] for m in g), derivedFrom=[m["id"] for m in g])
        by = {}
        for m in allm:
            if m["type"] in ("preference", "personal"):
                by.setdefault(m["domain"], []).append(m)
        for d, lst in by.items():
            if len(lst) >= 2:
                propose(type="invariant", content=f"Patron estable en {d}: " + "; ".join(m["content"] for m in lst),
                        derivedFrom=[m["id"] for m in lst])
        return created

    def approve(self, pid):
        p = self.proposals.get(pid)
        if not p or p["status"] != "proposed":
            raise MemoryError_(f"H-MEM: no hay propuesta pendiente {pid}")
        p["status"] = "approved"
        self.hm.ledger.log(pid, "dream_approved", self.hm.actor)
        return self.hm.store.add(p["content"], source="dreaming", layer="long_term", derivedFrom=p["derivedFrom"],
                                 provenance={"origin": "dreaming", "learnedAt": self.hm.clock(), "label": pid})


class HMEM:
    """Fachada H-MEM: add / query / feedback + servicios store, ledger, sleep, dreaming, conflicts."""

    def __init__(self, path: str | Path | None = None, clock=None, actor="midaz", strict_provenance=False):
        self.clock = clock or (lambda: int(time.time() * 1000))
        self.actor, self.path, self.strict_provenance = actor, Path(path) if path else None, strict_provenance
        self.ledger, self.store = TrustLedger(self), Store(self)
        self.retrieval, self.conflicts = Retrieval(self), Conflicts(self)
        self.sleep, self.dreaming, self.backups = Sleep(self), Dreaming(self), {}
        self._loading = False
        if self.path and self.path.exists():
            self._loading = True
            data = json.loads(self.path.read_text(encoding="utf-8"))
            for r in data["records"]:
                r["embedding"] = embed(r["content"])  # backfill (seccion 3)
                self.store.records[r["id"]] = r
            self.store.seq, self.ledger.entries = data["seq"], data["ledger"]
            self._loading = False

    def persist(self):
        if not self.path or self._loading:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        recs = [snapshot(r) for r in self.store.all()]
        self.path.write_text(json.dumps({"engine": "hmem", "seq": self.store.seq, "records": recs,
                                         "ledger": self.ledger.entries}, ensure_ascii=False, indent=1), encoding="utf-8")

    def add(self, content, source, **kw):
        return self.store.add(content, source, **kw)

    def query(self, q, **kw):
        return self.retrieval.query(q, **kw)

    def feedback(self, mid, kind):
        m = self.store.get(mid)
        if kind not in FEEDBACK_DELTAS or not m:
            raise MemoryError_(f"H-MEM: feedback invalido {kind!r} / {mid!r}")
        prev = snapshot(m)
        m["confidence"] = round(clamp01(m["confidence"] + FEEDBACK_DELTAS[kind]), 10)
        if kind == "helpful":
            m["accessCount"] += 1
        if kind == "wrong" and "review" not in m["tags"]:
            m["tags"].append("review")
        self.ledger.log(mid, "feedback", self.actor, previousState=prev, newState=snapshot(m), details={"kind": kind})
        self.persist()
        return m


# ---------- Funcion real de MIDAZ: memoria de decisiones del dueno (HU-14) ----------

def default_path() -> Path:
    return Path(os.environ.get("MIDAZ_HMEM_PATH", ROOT / "out" / "hmem" / "memoria.json"))


class DecisionMemory:
    """Decisiones del dueno sobre H-MEM. Cada recuerdo exige source (turno) y provenance (recibo o mensaje)."""

    def __init__(self, path=None, clock=None):
        self.hm = HMEM(path or default_path(), clock=clock, strict_provenance=True)

    def remember(self, decision: str, product_id: str, date: str, source: str, receipt_id: str | None = None,
                 owner_message: str | None = None):
        if not re.fullmatch(r"P\d{3}", product_id or "") or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date or ""):
            raise MemoryError_("H-MEM: decision necesita product_id P### y fecha AAAA-MM-DD")
        if not (receipt_id or owner_message):
            raise MemoryError_("H-MEM: decision sin provenance (recibo SQL o mensaje del dueno)")
        prov = ({"origin": "sql_receipt", "label": receipt_id, "receiptId": receipt_id} if receipt_id else
                {"origin": "owner_message", "label": owner_message})
        prov["learnedAt"] = self.hm.clock()
        return self.hm.add(f"{decision} {product_id} desde {date}", source=source, provenance=prov, type="factual",
                           layer="long_term", confidence=0.9, tags=[f"producto:{product_id}", f"fecha:{date}", "decision"])

    def recall(self, question: str):
        res = self.hm.query(question, threshold=0.0, topN=5)
        hits = [x for x in res["memories"] if "decision" in x["memory"]["tags"]]
        return hits, res


def answer_followup(question: str, memory: DecisionMemory, engine, run_query) -> dict:
    """HU-14: '¿Como me fue con lo de la Coca?' -> recuerdo H-MEM + recibo SQL antes/despues."""
    hits, res = memory.recall(question)
    if not hits:
        return {"answer": "No sé: no tengo ninguna decisión guardada sobre eso.", "memory": None, "receipt": None}
    m = hits[0]["memory"]
    pid = next(t.split(":", 1)[1] for t in m["tags"] if t.startswith("producto:"))
    fecha = next(t.split(":", 1)[1] for t in m["tags"] if t.startswith("fecha:"))
    q = run_query(engine, "40_antes_despues.sql", {"product_id": pid, "fecha": fecha})
    rows = {r[0]: r for r in q["rows"]}
    a, d = rows.get("antes"), rows.get("despues")
    if not a or not d:
        return {"answer": f"No sé: no hay ventas de {pid} antes y después de {fecha}.", "memory": m, "receipt": q}
    from .core import crc
    text = (f"Según lo que me dijo ({m['content']}; recuerdo {m['id']}, fuente {m['provenance']['label']}): "
            f"antes vendía {a[1]} unidades y dejaba {crc(a[2])}; después, {d[1]} unidades y {crc(d[2])} "
            f"de ganancia bruta, en ventanas de {a[3]} días.")
    return {"answer": text, "memory": m, "receipt": q, "trace": res["trace"]}
