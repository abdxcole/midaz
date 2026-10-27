"""run.py lee .env sin pisar el entorno y sin imprimir valores."""
import contextlib
import io
import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

import run


class TestCargarEnv(unittest.TestCase):
    def test_carga_sin_pisar_ni_imprimir(self):
        secreto = "sekrit-no-imprimir"
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / ".env"
            path.write_text(
                "\n".join([
                    "# comentario",
                    f"ZETARIS_API_KEY={secreto}-archivo",
                    'ZETARIS_REST_URL="http://localhost:8888/api/v1.0"',
                    "export ZETARIS_ORG_ID=org-demo",
                    "MIDAZ_ENGINE=",
                    "1MAL=no",
                    "SIN_IGUAL",
                    "",
                ]),
                encoding="utf-8",
            )
            buf, err = io.StringIO(), io.StringIO()
            with mock.patch.dict(os.environ, {"ZETARIS_API_KEY": secreto}, clear=False):
                os.environ.pop("ZETARIS_REST_URL", None)
                os.environ.pop("ZETARIS_ORG_ID", None)
                os.environ.pop("MIDAZ_ENGINE", None)
                with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
                    n = run.cargar_env(path)
                self.assertEqual(os.environ["ZETARIS_API_KEY"], secreto)
                self.assertEqual(os.environ["ZETARIS_REST_URL"], "http://localhost:8888/api/v1.0")
                self.assertEqual(os.environ["ZETARIS_ORG_ID"], "org-demo")
                self.assertNotIn("MIDAZ_ENGINE", os.environ)
                self.assertNotIn("1MAL", os.environ)
                self.assertGreaterEqual(n, 2)
            self.assertNotIn(secreto, buf.getvalue() + err.getvalue())

    def test_archivo_ausente(self):
        self.assertEqual(run.cargar_env(Path("/tmp/midaz-env-que-no-existe.env")), 0)

    def test_main_ui_ve_la_clave_antes_del_motor(self):
        secreto = "sekrit-no-imprimir"
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".env").write_text(
                f"ZETARIS_API_KEY={secreto}\nMIDAZ_ENGINE=zetaris\n", encoding="utf-8")
            visto = {}

            def fake_servir(engine):
                visto["name"] = engine.name
                visto["key"] = os.environ.get("ZETARIS_API_KEY")
                return 0

            limpio = {k: v for k, v in os.environ.items() if k not in ("ZETARIS_API_KEY", "MIDAZ_ENGINE")}
            buf, err = io.StringIO(), io.StringIO()
            with mock.patch.object(run, "ROOT", root), \
                 mock.patch.dict(os.environ, limpio, clear=True), \
                 mock.patch("midas.ui.servir", fake_servir), \
                 contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
                code = run.main(["run.py", "ui"])
            self.assertEqual(code, 0)
            self.assertEqual(visto["name"], "zetaris")
            self.assertEqual(visto["key"], secreto)
            self.assertNotIn(secreto, buf.getvalue() + err.getvalue())

    def test_sample_data_solo_si_el_motor_no_es_zetaris(self):
        local, zeta = mock.Mock(), mock.Mock()
        local.name, zeta.name = "sqlite-local-standin", "zetaris"
        self.assertEqual(run.anuncio_motor(local), "SAMPLE DATA - motor: sqlite-local-standin")
        self.assertEqual(run.anuncio_motor(zeta), "motor: zetaris")
        self.assertNotIn("SAMPLE DATA", run.anuncio_motor(zeta))

    def test_followup_zetaris_no_imprime_sample_data(self):
        eng = mock.Mock()
        eng.name = "zetaris"
        buf = io.StringIO()
        with mock.patch.object(run, "make_engine", return_value=eng), \
             mock.patch.object(run, "cargar_env"), \
             mock.patch.object(run, "run_followup", return_value={
                 "question": "q", "answer": "No sé", "receipt": None, "memory": None}), \
             contextlib.redirect_stdout(buf):
            run.main(["run.py", "followup"])
        self.assertNotIn("SAMPLE DATA", buf.getvalue())
        self.assertIn("motor: zetaris", buf.getvalue())
        eng.name = "sqlite-local-standin"
        buf = io.StringIO()
        with mock.patch.object(run, "make_engine", return_value=eng), \
             mock.patch.object(run, "cargar_env"), \
             mock.patch.object(run, "run_followup", return_value={
                 "question": "q", "answer": "No sé", "receipt": None, "memory": None}), \
             contextlib.redirect_stdout(buf):
            run.main(["run.py", "followup"])
        self.assertIn("SAMPLE DATA - motor: sqlite-local-standin", buf.getvalue())

    def test_comando_test_no_lee_env(self):
        with mock.patch.object(run, "cargar_env") as carga, \
             mock.patch("unittest.defaultTestLoader.discover"), \
             mock.patch("unittest.TextTestRunner") as runner:
            runner.return_value.run.return_value.wasSuccessful.return_value = True
            self.assertEqual(run.main(["run.py", "test"]), 0)
        carga.assert_not_called()
