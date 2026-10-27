"""HU-13: verificador. Re-ejecuta la SQL, compara filas y numeros; sin evidencia -> "No se"."""
import copy
import unittest

from midas.core import LocalEngine, build_answer
from midas.verifier import verify_answer


class _Engine:
    """Envuelve el motor local y permite romper la re-ejecucion."""
    name = "test"

    def __init__(self, base, mode=None):
        self.base, self.mode = base, mode

    def run(self, sql):
        if self.mode == "error":
            raise RuntimeError("motor caido")
        cols, rows, ms = self.base.run(sql)
        if self.mode == "empty":
            return cols, [], ms
        if self.mode == "changed":
            rows = [tuple((v + 1) if isinstance(v, (int, float)) and not isinstance(v, bool) else v for v in r)
                    for r in rows]
        return cols, rows, ms


class TestVerifier(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = LocalEngine()
        cls.ans = build_answer(cls.base)

    def fresh(self):
        return copy.deepcopy(self.ans)

    def test_todo_confirmado(self):
        a = verify_answer(self.base, self.fresh())
        self.assertEqual({r["verifier"]["verdict"] for r in a["receipts"]}, {"confirmado"})
        self.assertTrue(all(r["verifier"]["by"] and r["verifier"]["checked_at"] for r in a["receipts"]))
        self.assertEqual(a["verification"]["confirmados"], a["verification"]["total"])

    def test_numero_inventado_rechazado_y_no_se(self):
        a = self.fresh()
        a["receipts"][1]["claim"] = a["claims"][1]["text"] = "La ganancia fue de 999.999.999 colones."
        a = verify_answer(self.base, a)
        r = a["receipts"][1]
        self.assertEqual(r["verifier"]["verdict"], "rechazado")
        self.assertIn("999.999.999", r["verifier"]["notes"])
        self.assertTrue(a["claims"][1]["text"].startswith("No s\u00e9"))
        self.assertNotIn("999.999.999", a["claims"][1]["text"])

    def test_filas_cambiadas(self):
        a = verify_answer(_Engine(self.base, "changed"), self.fresh())
        self.assertIn("rechazado", {r["verifier"]["verdict"] for r in a["receipts"]})
        self.assertTrue(any("cambio" in (r["verifier"]["notes"] or "") for r in a["receipts"]))

    def test_motor_caido_todo_no_se(self):
        a = verify_answer(_Engine(self.base, "error"), self.fresh())
        self.assertEqual({r["verifier"]["verdict"] for r in a["receipts"]}, {"rechazado"})
        self.assertTrue(all(c["text"].startswith("No s\u00e9") for c in a["claims"]))
        self.assertEqual(a["verification"]["confirmados"], 0)
        # el error del motor queda solo en el recibo, nunca en el texto publico
        self.assertTrue(all("motor caido" in r["verifier"]["notes"] for r in a["receipts"]))
        self.assertNotIn("motor caido", a["answer"])
        self.assertEqual({c["text"] for c in a["claims"]}, {"No s\u00e9: no pude confirmar este dato con los datos."})

    def test_sin_filas_sin_evidencia(self):
        a = verify_answer(_Engine(self.base, "empty"), self.fresh())
        self.assertTrue(all("sin evidencia" in r["verifier"]["notes"] for r in a["receipts"]))


if __name__ == "__main__":
    unittest.main()