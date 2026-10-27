"""HU-01 (guardia de numeros + Nightshift), HU-04 (motor zetaris) y reglas de calidad en codigo."""
import copy
import subprocess
import sys
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from midas import calidad, nightshift, numguard
from midas.control import compare
from midas.core import DATA_DIR, LocalEngine, ZetarisEngine, build_answer, inline_view, load_sql, parse_zetaris_data, select_aliases, to_value


class TestNumGuard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        a = build_answer(LocalEngine())
        cls.results = a.pop("results")
        cls.ans = a
        cls.allowed = numguard.allowed_numbers(a, cls.results)

    def test_texto_deterministico_pasa(self):
        self.assertEqual([r for r in numguard.check(self.ans["answer"], self.allowed) if not r["keep"]], [])

    def test_rechaza_numero_inventado(self):
        txt = "El 20 % que más deja hace el 67,8 % [R-8020]. Este mes va a ganar ₡999.999 más."
        clean, rep = numguard.strike(txt, self.allowed)
        self.assertEqual([r["bad_numbers"] for r in rep if not r["keep"]], [["999.999"]])
        self.assertNotIn("999.999", clean)

    def test_formatos_cr_e_ingles(self):
        self.assertEqual(numguard.unsupported("Hace el 67.8 % y el 67,8 %.", self.allowed), [])
        self.assertEqual(numguard.unsupported("Faltaron ₡244.887.", self.allowed), [])
        self.assertEqual(numguard.unsupported("Faltaron ₡244.888.", self.allowed), ["244.888"])

    def test_cita_no_cuenta_como_numero(self):
        self.assertEqual(numguard.numbers_in("Texto [R-8020]."), [])


class TestNightshift(unittest.TestCase):
    def test_normaliza_url(self):
        for u in ("127.0.0.1:8088", "http://127.0.0.1:8088/v1", "http://127.0.0.1:8088/v1/chat/completions",
                  "http://127.0.0.1:8088/v1/models", "http://127.0.0.1:8088/healthz", "http://127.0.0.1:8088/"):
            self.assertEqual(nightshift.normalize_url(u), "http://127.0.0.1:8088/v1")

    def test_lane_fijo(self):
        for bad in ("meterless/auto", "meterless/text.auto", "", None):
            with self.assertRaises(nightshift.NightshiftError):
                nightshift.check_lane(bad)
        self.assertEqual(nightshift.check_lane("nvidia/nemotron-3.5-lightning-30b-a3b"),
                         "nvidia/nemotron-3.5-lightning-30b-a3b")

    def test_lee_token_de_env(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(nightshift.NightshiftError):
                nightshift._token()
        with mock.patch.dict(os.environ, {"METERLESS_RUNTIME_TOKEN": "x"}, clear=True):
            self.assertEqual(nightshift._token(), "x")

    def test_redact_tacha_y_anota_modelo(self):
        a = build_answer(LocalEngine())
        res = a.pop("results")
        sent = {}

        def fake(path, body):
            sent.update(path=path, body=body)
            return {"model": "nemotron-falso", "choices": [{"message": {"content":
                    "De 197 productos, 39 hacen el 67,8 % [R-8020]. Va a ganar ₡5.000.000 el mes que viene."}}]}
        out = nightshift.redact(a, res, lane="nemotron-lane-fijo", transport=fake)
        self.assertEqual(sent["path"], "/chat/completions")
        self.assertEqual(sent["body"]["model"], "nemotron-lane-fijo")
        self.assertNotIn("5.000.000", out["text"])
        self.assertEqual(len(out["struck"]), 1)
        self.assertTrue(out["text"].startswith("No s\u00e9: 3 productos"))
        self.assertTrue(all(r["redaccion"]["model"] == "nemotron-falso" for r in a["receipts"]))


class FakeZetaris:
    """Simula el REST de Zetaris: corre en SQLite y devuelve TODO como string (como Spark DECIMAL)."""

    def __init__(self):
        self.local, self.sqls = LocalEngine(), []

    def __call__(self, sql):
        self.sqls.append(sql)
        cols, rows, ms = self.local.run(sql)
        fmt = lambda v: None if v is None else (f"{v:.10E}" if isinstance(v, float) and abs(v) > 1e6 else str(v))
        return {"columns": [{"name": c} for c in cols], "rows": [[fmt(v) for v in r] for r in rows]}, ms


class TestZetarisEngine(unittest.TestCase):
    def test_check_pasa_con_motor_zetaris(self):
        fake = FakeZetaris()
        ans = build_answer(ZetarisEngine(run_sql=fake))
        self.assertEqual([c for c in compare(ans["results"]) if not c[1]], [])
        self.assertTrue(all(r["engine"] == "zetaris" for r in ans["receipts"]))
        self.assertTrue(any(s.startswith("WITH margen_por_producto AS") for s in fake.sqls))

    def test_inline_view_con_with_previo(self):
        sql = inline_view("WITH x AS (SELECT * FROM margen_por_producto) SELECT * FROM x")
        self.assertTrue(sql.startswith("WITH margen_por_producto AS ("))
        self.assertIn("),\nx AS (", sql)
        self.assertEqual(LocalEngine().run(sql)[1][:1] and len(LocalEngine().run(sql)[1]), 200)

    def test_conversion_strings(self):
        self.assertEqual(to_value("197"), 197)
        self.assertEqual(to_value("1.2089826E7"), 12089826.0)
        self.assertEqual(to_value("67.8"), 67.8)
        self.assertEqual(to_value("P001"), "P001")
        self.assertEqual(parse_zetaris_data([{"a": "1", "b": "x"}]), (["a", "b"], [(1, "x")]))


class TestCalidadEnCodigo(unittest.TestCase):
    def test_coincide_con_sql_datos_limpios(self):
        a = build_answer(LocalEngine())
        r = calidad.evaluar(*calidad.load_rows())
        self.assertEqual(calidad.comparar_con_sql(r, a["results"]["dq"]["rows"]), [])
        self.assertEqual(calidad.texto_no_se(r), a["claims"][0]["text"])
        self.assertTrue(calidad.bloquea(r))

    def test_coincide_con_sql_datos_sucios(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            for f in DATA_DIR.glob("*.csv"):
                shutil.copy(f, tmp / f.name)
            with open(tmp / "ventas_pos.csv", "a", encoding="utf-8") as f:
                f.write("2026-09-30,TX1,P001,1,100\n2026-09-30,TX2,P004,-2,3000\n,TX3,P005,1,\n")
            with open(tmp / "costos_inventario.csv", "a", encoding="utf-8") as f:
                f.write("P900,Producto raro,Otros,0,1\n")
            r = calidad.evaluar(*calidad.load_rows(tmp))
            self.assertEqual(r["precio_bajo_costo"]["productos"], ["P001"])
            self.assertEqual(r["ventas_negativas"]["productos"], ["P004"])
            self.assertEqual(r["costo_invalido"]["productos"], ["P900"])
            self.assertEqual(r["fila_incompleta"]["lineas"], 1)
            # SQL sin la fila incompleta (SQLite la carga con NULL y la cuenta distinto; se compara lo comun)
            with open(tmp / "ventas_pos.csv", encoding="utf-8") as f:
                lines = [l for l in f if not l.startswith(",TX3")]
            (tmp / "ventas_pos.csv").write_text("".join(lines), encoding="utf-8")
            r = calidad.evaluar(*calidad.load_rows(tmp))
            a = build_answer(LocalEngine(tmp))
            self.assertEqual(calidad.comparar_con_sql(r, a["results"]["dq"]["rows"]), [])
        finally:
            shutil.rmtree(tmp)


if __name__ == "__main__":
    unittest.main()


class FakeZetarisSinEncabezados(FakeZetaris):
    """Forma confirmada por Zetaris: `SELECT 1 AS one` -> [["1"]] (listas de texto, sin encabezados)."""

    def __call__(self, sql):
        data, ms = super().__call__(sql)
        return data["rows"], ms


class TestZetarisSinEncabezados(unittest.TestCase):
    def test_select_1_as_one(self):
        self.assertEqual(parse_zetaris_data([["1"]], "SELECT 1 AS one"), (["one"], [(1,)]))

    def test_alias_del_select_coinciden_con_local(self):
        root = Path(__file__).resolve().parent.parent / "sql"
        for f in sorted(root.glob("[0-9]*.sql")):
            raw = load_sql(f.name)
            if "{{" in raw or f.name.startswith("00_"):
                continue
            sql = inline_view(raw)
            self.assertEqual(select_aliases(sql), LocalEngine().run(sql)[0], f.name)

    def test_check_pasa_sin_encabezados(self):
        ans = build_answer(ZetarisEngine(run_sql=FakeZetarisSinEncabezados()))
        self.assertEqual([c for c in compare(ans["results"]) if not c[1]], [])


class TestRedactSinVariables(unittest.TestCase):
    def test_redact_sin_env_sale_limpio(self):
        root = Path(__file__).resolve().parent.parent
        env = {k: v for k, v in os.environ.items() if k not in (
            "NIGHTSHIFT_URL", "NIGHTSHIFT_TOKEN", "METERLESS_RUNTIME_TOKEN", "MIDAZ_NEMOTRON_LANE")}
        p = subprocess.run([sys.executable, str(root / "run.py"), "redact"], env=env,
                           capture_output=True, text=True, encoding="utf-8")
        self.assertNotEqual(p.returncode, 0)
        self.assertNotIn("Traceback", p.stderr + p.stdout)
        lines = [l for l in (p.stderr + p.stdout).splitlines() if l.strip()]
        self.assertEqual(len(lines), 1)
        self.assertIn("NIGHTSHIFT_URL", lines[0])


class TestZetarisSchemaMapDefault(unittest.TestCase):
    def test_default_map_only_for_zetaris(self):
        env = {k: v for k, v in os.environ.items() if k != "MIDAZ_SCHEMA_MAP"}
        with mock.patch.dict(os.environ, {**env, "MIDAZ_ENGINE": "zetaris"}, clear=True):
            sql = load_sql("00_margen_por_producto.sql")
            self.assertIn("midaz_pos.ventas_pos", sql)
            self.assertIn("midaz_inventario.costos_inventario", sql)
        with mock.patch.dict(os.environ, {**env, "MIDAZ_ENGINE": "local"}, clear=True):
            self.assertNotIn("midaz_pos.", load_sql("00_margen_por_producto.sql"))
        with mock.patch.dict(os.environ, {**env, "MIDAZ_ENGINE": "zetaris", "MIDAZ_SCHEMA_MAP": "pos=x"}, clear=True):
            self.assertIn("x.ventas_pos", load_sql("00_margen_por_producto.sql"))