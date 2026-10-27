"""E2E: el flujo de run.py usa H-MEM (answer_followup + DecisionMemory) para el seguimiento HU-14. SAMPLE DATA."""
import contextlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import run  # noqa: E402
from midas import memory  # noqa: E402


class TestRunFollowupE2E(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.root = self.tmp  # out/ del test, no toca el out/ real

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def _main(self, argv):
        buf = io.StringIO()
        with mock.patch.object(run, "ROOT", self.root), \
             mock.patch.object(memory, "answer_followup", wraps=memory.answer_followup) as spy, \
             mock.patch.dict("os.environ", {"MIDAZ_ENGINE": "local"}), contextlib.redirect_stdout(buf):
            code = run.main(argv)
        return code, buf.getvalue(), spy

    def test_followup_command_usa_hmem_y_recibo(self):
        code, out, spy = self._main(["run.py", "followup"])
        self.assertEqual(code, 0)
        self.assertEqual(spy.call_count, 1)
        self.assertIsInstance(spy.call_args.args[1], memory.DecisionMemory)
        self.assertIn("H-MEM", out)
        self.assertIn("sql/40_antes_despues.sql", out)
        self.assertTrue((self.root / "out" / "hmem" / "demo_memoria.json").exists())

    def test_demo_all_incluye_seguimiento_en_answer_json(self):
        code, out, spy = self._main(["run.py"])
        self.assertEqual(spy.call_count, 1)
        self.assertIn("seguimiento, H-MEM", out)
        f = json.loads((self.root / "out" / "answer.json").read_text(encoding="utf-8"))["followup"]
        self.assertEqual(f["engine"], "hmem")
        self.assertTrue(f["memory_id"])
        self.assertEqual(f["receipt"]["file"], "sql/40_antes_despues.sql")
        self.assertEqual([r[0] for r in f["receipt"]["rows"]], ["antes", "despues"])
        for _, unidades, _, _ in f["receipt"]["rows"]:  # numeros del texto salen del recibo
            self.assertIn(str(unidades), f["answer"])

    def test_memory_id_es_el_de_remember(self):
        with mock.patch.object(run, "ROOT", self.root):
            f = run.run_followup(run.make_engine())
        self.assertEqual(f["memory"]["id"], f["remembered_id"])

    def test_pregunta_no_relacionada_dice_no_se(self):
        code, out, spy = self._main(["run.py", "followup", "¿Cómo me fue con el arroz?"])
        self.assertEqual(spy.call_count, 0)
        self.assertIn("No sé", out)
        self.assertNotIn("sql/40_antes_despues.sql", out)
        self.assertEqual(code, 1)

    def test_pregunta_solo_con_fecha_dice_no_se(self):
        for q in ("¿Cómo me fue desde agosto?", "¿Cómo me fue desde el 15 de agosto de 2026?"):
            code, out, spy = self._main(["run.py", "followup", q])
            self.assertEqual(spy.call_count, 0, q)
            self.assertIn("No sé", out)
            self.assertNotIn("sql/40_antes_despues.sql", out)

    def test_falla_del_motor_da_no_se_sin_romper(self):
        eng = mock.Mock()
        eng.run.side_effect = RuntimeError("sql/40 sin verificar en Zetaris")
        with mock.patch.object(run, "ROOT", self.root):
            f = run.run_followup(eng)
        self.assertTrue(f["answer"].startswith("No sé"))
        self.assertIsNone(f["receipt"])
        self.assertEqual(f["error"], "RuntimeError")


if __name__ == "__main__":
    unittest.main()
