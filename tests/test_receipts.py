"""HU-03: toda frase con numero tiene recibo valido; calidad de datos dispara el "no se"."""
import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from midas.control import compare
from midas.core import DATA_DIR, LocalEngine, build_answer

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = json.loads((ROOT / "receipt" / "receipt.schema.json").read_text(encoding="utf-8"))
TYPES = {"string": str, "integer": int, "number": (int, float), "boolean": bool,
         "object": dict, "array": list, "null": type(None)}


def validate(obj, schema, path="$"):
    """Validador minimo (stdlib) para lo que usa receipt.schema.json."""
    errs = []
    t = schema.get("type")
    if t:
        ts = t if isinstance(t, list) else [t]
        ok = any(isinstance(obj, TYPES[x]) and not (x in ("integer", "number") and isinstance(obj, bool))
                 for x in ts)
        if not ok:
            return [f"{path}: tipo {type(obj).__name__}, se esperaba {t}"]
    if "enum" in schema and obj not in schema["enum"]:
        errs.append(f"{path}: {obj!r} no esta en {schema['enum']}")
    if isinstance(obj, str) and len(obj) < schema.get("minLength", 0):
        errs.append(f"{path}: vacio")
    if isinstance(obj, list) and len(obj) < schema.get("minItems", 0):
        errs.append(f"{path}: menos de {schema['minItems']} items")
    if isinstance(obj, dict):
        for k in schema.get("required", []):
            if k not in obj:
                errs.append(f"{path}.{k}: falta")
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            errs += [f"{path}.{k}: no permitido" for k in obj if k not in props]
        for k, v in obj.items():
            if k in props:
                errs += validate(v, props[k], f"{path}.{k}")
    if isinstance(obj, list) and "items" in schema:
        for i, v in enumerate(obj):
            errs += validate(v, schema["items"], f"{path}[{i}]")
    return errs


def claims_without_receipt(answer):
    ids = {r["id"] for r in answer["receipts"]}
    return [c["text"] for c in answer["claims"] if c.get("receipt_id") not in ids]


class TestReceipts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ans = build_answer(LocalEngine())

    def test_every_claim_has_receipt(self):
        self.assertTrue(self.ans["claims"])
        self.assertEqual(claims_without_receipt(self.ans), [])

    def test_answer_text_is_only_claims(self):
        # nada de texto suelto con numeros fuera de una frase con recibo
        self.assertEqual(self.ans["answer"], " ".join(c["text"] for c in self.ans["claims"]))

    def test_guard_detects_missing_receipt(self):
        bad = copy.deepcopy({k: v for k, v in self.ans.items() if k != "results"})
        bad["claims"].append({"text": "Gana 99 % en todo.", "receipt_id": None, "has_number": True})
        self.assertEqual(claims_without_receipt(bad), ["Gana 99 % en todo."])

    def test_receipts_match_schema(self):
        for r in self.ans["receipts"]:
            self.assertEqual(validate(r, SCHEMA), [], r["id"])
            self.assertGreater(r["row_count"], 0)

    def test_example_matches_schema(self):
        ex = json.loads((ROOT / "receipt" / "example.json").read_text(encoding="utf-8"))
        self.assertEqual(validate(ex, SCHEMA), [])

    def test_no_se_when_missing_cost(self):
        self.assertTrue(self.ans["answer"].startswith("No s\u00e9: 3 productos no tienen costo"))
        w = {x["code"]: x for x in self.ans["receipts"][0]["data_quality_warnings"]}
        self.assertEqual(w["sin_costo"]["products"], 3)

    def test_matches_control_sheet(self):
        failed = [c for c in compare(self.ans["results"]) if not c[1]]
        self.assertEqual(failed, [])


class TestDataQuality(unittest.TestCase):
    """Datos sucios a proposito: precio bajo costo y venta negativa deben salir como advertencia."""

    def test_dirty_data_warnings(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            for f in DATA_DIR.glob("*.csv"):
                shutil.copy(f, tmp / f.name)
            with open(tmp / "ventas_pos.csv", "a", encoding="utf-8") as f:
                f.write("2026-09-30,TX1,P001,1,100\n")      # arroz a 100 colones: bajo costo
                f.write("2026-09-30,TX2,P004,-2,3000\n")    # devolucion: venta negativa
            ans = build_answer(LocalEngine(tmp))
            codes = {w["code"]: w for w in ans["receipts"][0]["data_quality_warnings"]}
            self.assertIn("precio_bajo_costo", codes)
            self.assertIn("ventas_negativas", codes)
            self.assertEqual(codes["ventas_negativas"]["products"], 1)
            self.assertTrue(ans["answer"].startswith("No s\u00e9: 3 productos"))
        finally:
            shutil.rmtree(tmp)


if __name__ == "__main__":
    unittest.main()
