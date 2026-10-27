"""HU-15: motor H-MEM (Meterless) dentro de MIDAZ. Vectores oficiales + casos de 06-plan-midas 3.2.1."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from midas.core import LocalEngine, run_query
from midas.memory import DAY_MS, HMEM, DecisionMemory, MemoryError_, answer_followup

ROOT = Path(__file__).resolve().parent.parent
V = json.loads((ROOT / "midas" / "hmem_vectors" / "vectors.json").read_text(encoding="utf-8"))
T0 = V["clock"]


class TestConformanceVectors(unittest.TestCase):
    """Los vectores de engines/hmem/conformance/vectors (Meterless, commit 1742dec), en Python."""

    def test_record_validation(self):
        for c in V["sections"]["record-validation"]:
            hm = HMEM(clock=lambda: T0)
            if c["expect"] == "reject":
                with self.assertRaises(MemoryError_, msg=c["id"]):
                    hm.add(c["input"]["content"], source=c["input"]["source"])
            else:
                self.assertTrue(hm.add(c["input"]["content"], source=c["input"]["source"])["id"])

    def test_feedback_deltas(self):
        for c in V["sections"]["feedback-deltas"]:
            hm = HMEM(clock=lambda: T0)
            m = hm.add("record under feedback", source="conformance", confidence=c["start"])
            acc = m["accessCount"]
            hm.feedback(m["id"], c["kind"])
            self.assertAlmostEqual(m["confidence"], c["expectConfidence"], places=6, msg=c["id"])
            if "expectAccessDelta" in c:
                self.assertEqual(m["accessCount"] - acc, c["expectAccessDelta"], c["id"])
            if "expectTag" in c:
                self.assertIn(c["expectTag"], m["tags"], c["id"])

    def test_ranking_order(self):
        for c in V["sections"]["ranking-order"]:
            hm = HMEM(clock=lambda: T0)
            k = {r["key"]: hm.add(r["content"], source="conformance", confidence=r["confidence"], layer=r["layer"])
                 for r in c["records"]}
            for r in c["records"]:
                if r.get("supersededByKey"):
                    k[r["key"]]["supersededBy"] = k[r["supersededByKey"]]["id"]
            order = [x["memory"]["id"] for x in hm.query(c["query"], threshold=0, topN=10)["memories"]]
            exp = [k[x]["id"] for x in c["expectOrder"]]
            self.assertEqual([i for i in order if i in exp], exp, c["id"])

    def test_sleep_guardrails(self):
        for c in V["sections"]["sleep-guardrails"]:
            now = [T0]
            hm = HMEM(clock=lambda: now[0])
            k = {r["key"]: hm.add(r["content"], source=r["source"], derivedFrom=r.get("derivedFrom")) for r in c["records"]}
            now[0] = T0 + c["ageDays"] * DAY_MS
            before = sorted(m["id"] for m in hm.store.all())
            plan = hm.sleep.preview()
            self.assertEqual(sorted(m["id"] for m in hm.store.all()), before, "preview no muta")
            for x in c["expectArchived"]:
                self.assertIn(k[x]["id"], plan["toArchive"])
            for x in c["expectProtected"]:
                self.assertNotIn(k[x]["id"], plan["toArchive"])
            rep = hm.sleep.execute(plan)
            for x in c["expectProtected"]:
                self.assertIsNotNone(hm.store.get(k[x]["id"]))
            self.assertTrue(rep["backupId"])

    def test_conflict_gate(self):
        for c in V["sections"]["conflict-gate"]:
            hm = HMEM(clock=lambda: T0)
            a = hm.add(c["a"]["content"], source="conformance", confidence=c["a"]["confidence"])
            b = hm.add(c["b"]["content"], source="conformance", confidence=c["b"]["confidence"])
            found = hm.conflicts.scan()
            self.assertTrue(found)
            out = hm.conflicts.auto_resolve(found[0])
            self.assertIn(out, ("resolved", "queued"))
            if out == "resolved":
                self.assertTrue(a["supersededBy"] or b["supersededBy"])
            self.assertIsNotNone(hm.store.get(a["id"]))
            self.assertIsNotNone(hm.store.get(b["id"]))

    def test_ledger_audit(self):
        for c in V["sections"]["ledger-audit"]:
            hm = HMEM(clock=lambda: T0)
            m = hm.add("audited record", source="conformance", confidence=c["start"])
            hm.feedback(m["id"], c["kind"])
            h = hm.ledger.history(m["id"])
            self.assertEqual([e["action"] for e in h], c["expectActions"])
            self.assertAlmostEqual(h[-1]["previousState"]["confidence"], c["expectPrev"])
            self.assertAlmostEqual(h[-1]["newState"]["confidence"], c["expectNew"])

    def test_dream_boundary(self):
        for c in V["sections"]["dream-boundary"]:
            hm = HMEM(clock=lambda: T0)
            for r in c["records"]:
                hm.add(r["content"], source="conformance", type=r["type"])
            n = len(hm.store.all())
            props = hm.dreaming.dream()
            self.assertTrue(props)
            self.assertEqual(len(hm.store.all()), n, "nada se materializa antes de aprobar")
            created = hm.dreaming.approve(props[0]["id"])
            self.assertEqual(created["layer"], "long_term")
            self.assertTrue(created["derivedFrom"])


class TestDecisionMemory(unittest.TestCase):
    """Casos minimos de docs/06-plan-midas.md 3.2.1."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.path = self.tmp / "memoria.json"

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def _coca(self, mem):
        return mem.remember("Subí el precio de la Coca-Cola 2.5 L", "P003", "2026-08-15",
                            source="chat turno 1: 'subí la Coca el 15 de agosto'",
                            owner_message="Doña Marta: subí la Coca el 15 de agosto")

    def test_1_guarda_y_recupera_en_otra_instancia(self):
        m = self._coca(DecisionMemory(self.path))
        otra = DecisionMemory(self.path)  # reinicio del proceso: se lee del JSON
        hits, _ = otra.recall("¿Cómo me fue con lo de la Coca?")
        self.assertTrue(hits)
        self.assertEqual(hits[0]["memory"]["id"], m["id"])
        self.assertEqual(hits[0]["memory"]["provenance"]["origin"], "owner_message")
        self.assertIn("create", [e["action"] for e in otra.hm.ledger.history(m["id"])])

    def test_2_rechaza_sin_source_o_provenance(self):
        mem = DecisionMemory(self.path)
        with self.assertRaises(MemoryError_):
            mem.remember("Subí la Coca", "P003", "2026-08-15", source="")
        with self.assertRaises(MemoryError_):
            mem.remember("Subí la Coca", "P003", "2026-08-15", source="chat")  # sin recibo ni mensaje
        with self.assertRaises(MemoryError_):
            mem.hm.add("algo", source="chat", provenance={"origin": "inventado"})
        self.assertEqual(mem.hm.store.all(), [])

    def test_3_respuesta_hu14_cita_recuerdo_y_recibo(self):
        m = self._coca(DecisionMemory(self.path))
        mem = DecisionMemory(self.path)
        out = answer_followup("¿Cómo me fue con lo de la Coca?", mem, LocalEngine(), run_query)
        self.assertIn(m["id"], out["answer"])
        self.assertEqual(out["receipt"]["file"], "sql/40_antes_despues.sql")
        self.assertIn("'P003'", out["receipt"]["sql"])
        self.assertEqual([r[0] for r in out["receipt"]["rows"]], ["antes", "despues"])
        # los numeros del texto salen de las filas del recibo
        for _, unidades, _, _ in out["receipt"]["rows"]:
            self.assertIn(str(unidades), out["answer"])

    def test_sin_memoria_dice_no_se(self):
        out = answer_followup("¿Cómo me fue con lo de la Coca?", DecisionMemory(self.path), LocalEngine(), run_query)
        self.assertTrue(out["answer"].startswith("No sé"))


if __name__ == "__main__":
    unittest.main()
