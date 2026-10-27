"""Golden set: each expected_answer in tests/golden.yaml is re-computed from the repo data.

SAMPLE DATA. Stdlib only (no PyYAML): golden.yaml is read with a small parser that
handles the flat "items:" list used in that file. Numbers are taken from the
expected_answer text itself, so golden.yaml stays the single source of truth.
"""
import re
import unittest
from pathlib import Path

from midas.core import LocalEngine, load_sql

ROOT = Path(__file__).resolve().parent.parent
GOLDEN = ROOT / "tests" / "golden.yaml"


def load_golden(path=GOLDEN):
    items, cur = [], None
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = re.match(r"^\s*(-\s+)?([a-z_]+):\s*(.*)$", line)
        if not m or line.startswith(("version", "data_status", "items")):
            continue
        if m.group(1):
            cur = {}
            items.append(cur)
        val = m.group(3).strip()
        if val.startswith('"') and val.endswith('"'):
            val = val[1:-1]
        elif val in ("true", "false"):
            val = val == "true"
        cur[m.group(2)] = val
    return {it["id"]: it for it in items}


def numbers(text):
    """All numbers in a text, '12,089,826' -> 12089826.0, '67.8%' -> 67.8."""
    return [float(x.replace(",", "")) for x in re.findall(r"\d[\d,]*(?:\.\d+)?", text)]


class GoldenSet(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g = load_golden()
        cls.e = LocalEngine()

    def q(self, name):
        return self.e.run(load_sql(name))[1]

    def sql(self, text):
        return self.e.run(text)[1]

    def assertAt(self, item_id, pos, value, tol):
        """The number at position `pos` of the item's expected_answer must equal value within tol.

        Positions count every number in the text in reading order (product codes and sizes
        included), so a value can only match the slot it is meant for.
        """
        nums = numbers(self.g[item_id]["expected_answer"])
        self.assertLess(pos, len(nums), f"{item_id}: no number at position {pos} in {nums}")
        self.assertLessEqual(abs(nums[pos] - value), tol,
                             f"{item_id}[{pos}]: computed {value}, expected {nums[pos]} (tol {tol})")

    def test_structure(self):
        self.assertEqual(len(self.g), 15)
        for it in self.g.values():
            for k in ("question", "expected_answer", "expected_sql_or_source", "tolerance"):
                self.assertTrue(it.get(k), f"{it['id']} missing {k}")
            for path in re.findall(r"(?:sql|data/output)/[\w./]+\.(?:sql|csv|md)", it["expected_sql_or_source"]):
                self.assertTrue((ROOT / path).exists(), f"{it['id']}: {path} not in repo")
        self.assertEqual(sum(1 for it in self.g.values() if it.get("expects_no_evidence")), 2)

    def test_G01_G04_8020(self):
        n, total, n_top, pct_top, n80, pct80 = self.q("11_hu02_8020_resumen.sql")[0]
        self.assertAt("G01", 0, pct_top, 0.1)
        self.assertAt("G01", 1, n_top, 0)
        self.assertAt("G01", 2, n, 0)
        self.assertAt("G02", 0, n, 0)
        self.assertAt("G03", 0, total, 1)
        self.assertAt("G04", 0, n80, 0)
        self.assertAt("G04", 1, pct80, 0.1)

    def test_G05_G06_ranking(self):
        rows = self.q("10_hu02_8020_ranking.sql")
        top = rows[0]
        self.assertIn(top[2], self.g["G05"]["expected_answer"])
        self.assertIn(top[3], self.g["G05"]["expected_answer"])
        self.assertAt("G05", 2, top[7], 1)
        expected = [x.strip() for x in self.g["G06"]["expected_answer"].split(";")]
        self.assertEqual([r[3] for r in rows[:5]], expected)

    def test_G07_G08_volume_vs_profit(self):
        rows = {r[3]: r for r in self.q("20_vende_mucho_deja_poco.sql")}
        rice = rows["P001"]
        self.assertEqual(rice[0], 1)
        self.assertIn(rice[4], self.g["G07"]["expected_answer"])
        self.assertAt("G07", 4, rice[1], 0)
        self.assertAt("G07", 3, rice[5], 0)
        self.assertAt("G07", 5, rice[6], 1)
        self.assertAt("G08", 0, rice[7], 0.1)
        self.assertAt("G08", 1, rows["P004"][7], 0.1)

    def test_G09_coca_cola_price(self):
        rows = {r[0]: r for r in self.q("32_precio_coca_cola.sql")}
        a, d = rows["antes"], rows["despues"]
        self.assertEqual((a[1], a[2]), (1650.0, 1650.0))
        self.assertEqual((d[1], d[2]), (1850.0, 1850.0))
        for i, r in enumerate((a, d)):
            self.assertAt("G09", 0 + i, r[1], 0)
            self.assertAt("G09", 2 + i, r[5], 0.1)
            self.assertAt("G09", 4 + i, r[7], 1)

    def test_G10_G11_shortfall(self):
        rows = {r[0]: r for r in self.q("30_me_alcanza.sql")}
        sep = rows["2026-09"]
        self.assertGreater(sep[3], 0)
        self.assertAt("G10", 1, sep[1], 1)
        self.assertAt("G10", 0, sep[2], 1)
        self.assertAt("G10", 2, sep[3], 1)
        self.assertAt("G11", 0, rows["2026-07"][3], 1)
        self.assertAt("G11", 1, rows["2026-08"][3], 1)

    def test_G12_largest_expense(self):
        rows = self.sql("SELECT concept, amount FROM finanzas.gastos_operativos "
                        "WHERE month = '2026-09' ORDER BY amount DESC")
        self.assertTrue(rows[0][0].startswith("Planilla 4 empleados"))
        self.assertAt("G12", 0, 4, 0)  # "4 employees" in the concept text
        self.assertAt("G12", 1, rows[0][1], 0)
        self.assertAt("G12", 2, sum(r[1] for r in rows), 0)

    def test_G13_category(self):
        cat, _, profit = self.q("33_margen_por_categoria.sql")[0]
        self.assertIn(cat, self.g["G13"]["expected_answer"])
        self.assertAt("G13", 0, profit, 1)

    def test_G14_no_cost_means_no_profit(self):
        """'No data' case: meats have sales but no cost row, so profit must be unknown (NULL)."""
        self.assertTrue(self.g["G14"].get("expects_no_evidence"))
        view = {r[0]: r for r in self.sql(
            "SELECT product_id, sin_costo, ganancia_bruta FROM margen_por_producto")}
        for pid in ("P007", "P008", "P009"):
            self.assertEqual(view[pid][1], 1)
            self.assertIsNone(view[pid][2], f"{pid}: profit must be NULL, never a number")
        detail = {r[0]: r for r in self.q("02_sin_costo_detalle.sql")}
        self.assertEqual(len(detail), 3)
        self.assertAt("G14", 1, detail["P007"][1], 0)
        self.assertAt("G14", 2, detail["P007"][2], 1)

    def test_G15_no_october_data(self):
        """'No data' case: nothing after 2026-09, so an October figure cannot come from data."""
        self.assertTrue(self.g["G15"].get("expects_no_evidence"))
        self.assertEqual(self.sql("SELECT MAX(date) FROM pos.ventas_pos")[0][0], "2026-09-30")
        self.assertEqual(self.sql("SELECT MAX(month) FROM finanzas.gastos_operativos")[0][0], "2026-09")
        self.assertNotIn("2026-10", [r[0] for r in self.q("30_me_alcanza.sql")])


if __name__ == "__main__":
    unittest.main()
