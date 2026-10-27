#!/usr/bin/env python3
"""MIDAZ - un solo comando (Sprint 1, sin Docker). SAMPLE DATA.

  python run.py          corre SQL en el sustituto local, imprime la respuesta con recibos,
                         escribe out/answer.json y compara contra la hoja de control
  python run.py ui       pantalla local (stdlib) para el video del pitch
  python run.py test     corre los tests (unittest); no lee .env
  python run.py check    solo la comparacion contra control (exit 1 si algo no coincide)
  python run.py redact   ademas, Nemotron via Nightshift redacta desde answer.json (lane fijo)
  python run.py followup ["pregunta"]   solo el seguimiento HU-14 con memoria H-MEM (tambien corre en `all`)

  Motor: MIDAZ_ENGINE=local (sustituto SQLite, por defecto) | zetaris (REST, ver docs/08-hu00-zetaris.md)
  Si existe .env junto a este archivo, se carga sin pisar variables ya definidas y sin imprimir valores.
"""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from midas.control import compare  # noqa: E402
from midas.core import build_answer, make_engine  # noqa: E402


def cargar_env(path=None) -> int:
    """Lee KEY=VALUE de un .env si el archivo existe.

    No pisa variables que ya están en el entorno y no imprime nombres ni valores.
    Un valor vacío no se carga (un .env copiado del ejemplo no deja claves en blanco).
    Devuelve cuántas variables nuevas quedaron definidas.
    """
    import os
    import re
    path = Path(path) if path is not None else ROOT / ".env"
    if not path.is_file():
        return 0
    n = 0
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].strip()
        if "=" not in line:
            continue
        key, val = line.split("=", 1)
        key = key.strip()
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key) or key in os.environ:
            continue
        val = val.strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "'\"":
            val = val[1:-1]
        if val == "":
            continue
        os.environ[key] = val
        n += 1
    return n


def faltan_vars_nightshift(env=None) -> str | None:
    """Primera variable de Nightshift que falta (o None). Solo revisa nombres, nunca imprime valores."""
    import os
    env = os.environ if env is None else env
    if not env.get("NIGHTSHIFT_URL"):
        return "NIGHTSHIFT_URL"
    if not (env.get("NIGHTSHIFT_TOKEN") or env.get("METERLESS_RUNTIME_TOKEN")):
        return "NIGHTSHIFT_TOKEN (o METERLESS_RUNTIME_TOKEN)"
    if not env.get("MIDAZ_NEMOTRON_LANE"):
        return "MIDAZ_NEMOTRON_LANE"
    return None


FOLLOWUP_Q = "¿Cómo me fue con lo de la Coca?"
# Turno guionado del demo (SAMPLE DATA, mismo caso que tests/test_hmem.py): el dueno cuenta una decision.
DEMO_DECISION = dict(decision="Subí el precio de la Coca-Cola 2.5 L", product_id="P003", date="2026-08-15",
                     source="demo turno 1: 'subí la Coca el 15 de agosto'",
                     owner_message="Dueña (demo): subí la Coca el 15 de agosto")


_STOP = {"como", "fue", "con", "que", "tal", "les", "los", "las", "del", "una", "uno", "eso", "esto", "esa", "ese",
         "cuando", "cuanto", "despues", "antes", "precio", "decision", "producto", "productos", "ahora",
         "desde", "hasta", "dia", "dias", "semana", "semanas", "mes", "meses", "ano", "anos", "hoy", "ayer",
         "enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "setiembre",
         "octubre", "noviembre", "diciembre"}


def _palabras(texto: str) -> set[str]:
    import re
    import unicodedata
    t = unicodedata.normalize("NFKD", texto.lower()).encode("ascii", "ignore").decode()
    return {w for w in re.findall(r"[a-z0-9]+", t) if len(w) >= 3 and w not in _STOP and not w.isdigit()}


def recuerdo_coincide(question: str, memoria: dict) -> bool:
    """Evita el falso positivo de recall(threshold=0.0): la pregunta debe nombrar algo del recuerdo
    (p. ej. 'Coca' en 'Coca-Cola 2.5 L'). Si no, se responde 'No sé'."""
    return bool(_palabras(question) & _palabras(memoria["content"]))


def run_followup(engine, question=FOLLOWUP_Q, mem_path=None) -> dict:
    """Envoltura segura: cualquier falla (p. ej. sql/40 aun sin verificar en Zetaris) da 'No sé', no rompe el demo."""
    try:
        return _run_followup(engine, question, mem_path)
    except Exception as e:  # noqa: BLE001
        return {"answer": f"No sé: no pude responder el seguimiento ({type(e).__name__}).", "memory": None,
                "receipt": None, "engine": "hmem", "question": question, "error": type(e).__name__}


def _run_followup(engine, question=FOLLOWUP_Q, mem_path=None) -> dict:
    """HU-14 en el flujo del demo: guarda la decision en H-MEM y responde el seguimiento con
    answer_followup() (recuerdo H-MEM + recibo sql/40_antes_despues.sql). Memoria del demo se reinicia en cada corrida."""
    from midas.core import run_query
    from midas.memory import DecisionMemory, answer_followup
    path = Path(mem_path) if mem_path else ROOT / "out" / "hmem" / "demo_memoria.json"
    if path.exists():
        path.unlink()
    recordado = DecisionMemory(path).remember(**DEMO_DECISION)
    mem = DecisionMemory(path)  # otra instancia: lee de disco
    hits, _ = mem.recall(question)
    if not hits or not recuerdo_coincide(question, hits[0]["memory"]):
        out = {"answer": "No sé: no tengo ninguna decisión guardada sobre eso.", "memory": None, "receipt": None}
    else:
        out = answer_followup(question, mem, engine, run_query)
    out["remembered_id"] = recordado["id"]
    out["engine"] = "hmem"
    out["question"] = question
    return out


def anuncio_motor(engine) -> str:
    """Línea de arranque. «SAMPLE DATA» solo en el sustituto local, no con Zetaris."""
    linea = f"motor: {getattr(engine, 'name', '')}"
    if getattr(engine, "name", "") == "zetaris":
        return linea
    return f"SAMPLE DATA - {linea}"


def print_followup(f):
    print(f"\nP (seguimiento, H-MEM): {f['question']}\n  - {f['answer']}")
    if f["receipt"]:
        q = f["receipt"]
        print(f"      recibo: {q['file']}, {len(q['rows'])} filas, {round(q['ms'], 2)} ms; recuerdo H-MEM {f['memory']['id']}")


def main(argv):
    for stream in (sys.stdout, sys.stderr):  # consola Windows cp1252: no romper con colones/tildes
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    cmd = argv[1] if len(argv) > 1 else "all"
    # `test` no lee .env: la suite tiene que seguir igual en la máquina del equipo,
    # donde ese archivo puede fijar MIDAZ_ENGINE=zetaris.
    if cmd != "test":
        cargar_env()
    if cmd == "test":
        suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), top_level_dir=str(ROOT))
        return 0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1

    if cmd == "redact":
        falta = faltan_vars_nightshift()
        if falta:
            print(f"Error: falta la variable de entorno {falta} (ver docs/11 y el .env local); no se llamo a Nightshift.",
                  file=sys.stderr)
            return 2

    engine = make_engine()
    if cmd == "ui":
        from midas.ui import servir
        return servir(engine)
    if cmd == "followup":
        f = run_followup(engine, argv[2] if len(argv) > 2 else FOLLOWUP_Q)
        print(anuncio_motor(engine))
        print_followup(f)
        return 0 if f["receipt"] else 1
    ans = build_answer(engine)
    from midas.verifier import verify_answer  # HU-13: veredicto real por recibo; sin evidencia -> No se
    verify_answer(engine, ans)
    if cmd in ("all", "redact"):
        print(anuncio_motor(engine) + "\n")
        print("P:", ans["question"])
        for c in ans["claims"]:
            r = next(x for x in ans["receipts"] if x["id"] == c["receipt_id"])
            print(f"  - {c['text']}\n      recibo {r['id']}: {r['sql_file']}, {r['row_count']} filas, "
                  f"{r['execution_ms']} ms, veredicto={r['verifier']['verdict']}")
        out = ROOT / "out"
        out.mkdir(exist_ok=True)
        public = {k: v for k, v in ans.items() if k != "results"}
        f = run_followup(engine)
        print_followup(f)
        public["followup"] = {"question": f["question"], "answer": f["answer"], "engine": "hmem",
                              "memory_id": f["memory"]["id"] if f["memory"] else None,
                              "receipt": {k: f["receipt"][k] for k in ("file", "sql", "columns", "rows", "ms")}
                              if f["receipt"] else None}
        if cmd == "redact":
            from midas.nightshift import NightshiftError, redact
            try:
                out_r = redact(public, ans["results"])
            except NightshiftError as e:
                print(f"Error de Nightshift: {e}", file=sys.stderr)
                return 2
            print(f"Nemotron ({out_r['model']}, lane {out_r['meta']['lane']}):\n  {out_r['text']}")
            for s in out_r["struck"]:
                print(f"  [TACHADA] {s['sentence']} (numeros sin recibo: {s['bad_numbers']})")
            public["answer_redactada"] = out_r["text"]
        (out / "answer.json").write_text(json.dumps(public, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nRecibos completos: {out / 'answer.json'}\n")

    v = ans["verification"]
    print(f"Verificador: {v['confirmados']}/{v['total']} frases confirmadas (SQL re-ejecutada en {engine.name})")
    checks = compare(ans["results"])
    print("Hoja de control (data/output/control_8020):")
    for name, ok, detail in checks:
        print(f"  [{'OK ' if ok else 'MAL'}] {name}: {detail}")
    from midas import calidad  # reglas de calidad en codigo vs SQL (solo con datos locales)
    diffs = calidad.comparar_con_sql(calidad.evaluar(*calidad.load_rows()), ans["results"]["dq"]["rows"])
    checks.append(("calidad_codigo_vs_sql", not diffs, "; ".join(diffs) or "coinciden"))
    print(f"  [{'OK ' if not diffs else 'MAL'}] calidad_codigo_vs_sql: {'; '.join(diffs) or 'coinciden'}")
    failed = [c for c in checks if not c[1]]
    print(f"\n{len(checks) - len(failed)}/{len(checks)} coinciden.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
