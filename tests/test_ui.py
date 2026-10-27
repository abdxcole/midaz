"""Pantalla local: el endpoint reutiliza el motor y no muestra llaves ni errores."""
import json
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

from midas.core import LocalEngine
from midas.ui import (
    _Servidor,
    clasificar,
    fuentes_visibles,
    linea_arranque,
    pagina,
    responder,
)
from midas.verifier import NO_SE


class _MotorRoto:
    name = "zetaris"

    def run(self, sql):
        raise RuntimeError("ZETARIS_API_KEY=super-secret-token no conecta")


class TestClasificarYFuentes(unittest.TestCase):
    def test_ejemplos_y_lo_que_no_sabemos(self):
        self.assertEqual(clasificar("¿Qué productos me dan la plata?"), "plata")
        self.assertEqual(clasificar("¿Me alcanza este mes?"), "alcanza")
        self.assertEqual(clasificar("¿Cómo me fue con lo de la Coca?"), "seguimiento")
        self.assertEqual(clasificar("¿Cuánto deja la carne molida?"), "carne")
        self.assertEqual(clasificar("¿Me alcanza en octubre?"), "fuera")
        self.assertEqual(clasificar("¿Qué tiempo hará mañana?"), "fuera")
        self.assertEqual(clasificar("   "), "vacia")

    def test_fuentes_zetaris_salen_del_sql(self):
        fuentes = fuentes_visibles({
            "sql": "SELECT 1 FROM midaz_pos.ventas_pos v JOIN midaz_inventario.costos_inventario c",
            "view": {"definition_sql": "FROM midaz_finanzas.gastos_operativos"},
            "sources": [],
        })
        self.assertEqual(
            [f["nombre"] for f in fuentes],
            ["midaz_pos.ventas_pos", "midaz_inventario.costos_inventario", "midaz_finanzas.gastos_operativos"],
        )
        self.assertEqual([f["origen"] for f in fuentes], ["POS", "Inventario", "Finanzas"])

    def test_arranque_sample_data_solo_sin_zetaris(self):
        url = "http://127.0.0.1:8765"
        local, zeta = mock.Mock(), mock.Mock()
        local.name, zeta.name = "sqlite-local-standin", "zetaris"
        self.assertIn("SAMPLE DATA", linea_arranque(local, url))
        self.assertNotIn("SAMPLE DATA", linea_arranque(zeta, url))
        self.assertIn(url, linea_arranque(zeta, url))

    def test_la_pagina_no_trae_answer_json(self):
        html = pagina({"ejemplos": [], "motor": "Local, sin Zetaris", "muestra": True, "memoria": []})
        self.assertIn("Datos de ejemplo", html)
        self.assertIn("Memoria H-MEM", html)
        self.assertNotIn("answer.json", html)
        self.assertNotIn("ZETARIS_API_KEY", html)


class TestResponder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = LocalEngine()
        cls.tmp = TemporaryDirectory()
        cls.mem = Path(cls.tmp.name) / "mem.json"

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def _preguntar(self, texto, engine=None):
        return responder(engine or self.engine, texto, self.mem)

    def test_plata_confirmada_con_fuentes_y_filas(self):
        out = self._preguntar("¿Qué productos me dan la plata?")
        self.assertEqual(out["sello"], "confirmado")
        self.assertEqual(out["sello_texto"], "Confirmado")
        self.assertIn("%", out["respuesta"])
        self.assertTrue(out["muestra"])
        self.assertEqual(out["motor"], "Local, sin Zetaris")
        nombres = {f["nombre"] for p in out["pruebas"] for f in p["fuentes"]}
        self.assertIn("pos.ventas_pos", nombres)
        self.assertIn("inventario.costos_inventario", nombres)
        self.assertNotIn("finanzas.gastos_operativos", nombres)
        self.assertTrue(any(p["filas"] and p["sql"].strip() for p in out["pruebas"]))
        self.assertTrue(any(p["filas_total"] > len(p["filas"]) for p in out["pruebas"]))
        blob = json.dumps(out)
        self.assertNotIn("answer.json", blob)
        self.assertNotIn("notes", blob)
        self.assertNotIn("ZETARIS_API_KEY", blob)
        self.assertEqual(set(out), {
            "pregunta", "respuesta", "sello", "sello_texto", "muestra", "motor", "pruebas", "memoria"})

    def test_alcanza_nombra_finanzas(self):
        out = self._preguntar("¿Me alcanza este mes?")
        self.assertEqual(out["sello"], "confirmado")
        nombres = {f["nombre"] for p in out["pruebas"] for f in p["fuentes"]}
        self.assertIn("finanzas.gastos_operativos", nombres)
        self.assertIn("pos.ventas_pos", nombres)

    def test_carne_dice_no_se_y_el_verificador_confirma(self):
        out = self._preguntar("¿Cuánto deja la carne molida?")
        self.assertTrue(out["respuesta"].startswith("No sé"))
        self.assertEqual(out["sello"], "confirmado")
        self.assertEqual(out["pruebas"][0]["sello"], "confirmado")
        self.assertTrue(out["pruebas"][0]["filas"])

    def test_coca_sella_la_frase_del_sql_y_muestra_memoria(self):
        out = self._preguntar("¿Cómo me fue con lo de la Coca?")
        self.assertEqual(out["sello"], "confirmado")
        self.assertEqual(out["pruebas"][0]["archivo"], "sql/40_antes_despues.sql")
        antes = next(f for f in out["pruebas"][0]["filas"] if f[0] == "antes")
        self.assertIn(str(antes[1]), out["respuesta"])
        self.assertNotIn("2026", out["respuesta"])
        self.assertEqual(
            {f["nombre"] for f in out["pruebas"][0]["fuentes"]},
            {"pos.ventas_pos", "inventario.costos_inventario"})
        self.assertTrue(any("Coca" in m["texto"] for m in out["memoria"]))
        self.assertIn("2026", out["memoria"][0]["texto"])

    def test_fuera_de_alcance_y_agosto_sin_producto(self):
        fuera = self._preguntar("¿Me alcanza en octubre?")
        self.assertEqual(fuera["sello"], "no_se")
        self.assertEqual(fuera["respuesta"], NO_SE)
        self.assertEqual(fuera["pruebas"], [])
        arroz = self._preguntar("¿Cómo me fue desde agosto?")
        self.assertEqual(arroz["sello"], "no_se")
        self.assertFalse(arroz["pruebas"])

    def test_error_de_motor_no_llega_a_la_pantalla(self):
        with mock.patch.dict("os.environ", {"ZETARIS_API_KEY": "clave-que-no-puede-verse"}):
            out = self._preguntar("¿Qué productos me dan la plata?", _MotorRoto())
        blob = json.dumps(out)
        self.assertEqual(out["sello"], "no_se")
        self.assertEqual(out["respuesta"], NO_SE)
        self.assertNotIn("super-secret-token", blob)
        self.assertNotIn("RuntimeError", blob)
        self.assertNotIn("clave-que-no-puede-verse", blob)
        self.assertNotIn("ZETARIS_API_KEY", blob)
        self.assertNotIn("Traceback", blob)

    def test_seguimiento_roto_tampoco_filtra(self):
        out = self._preguntar("¿Cómo me fue con lo de la Coca?", _MotorRoto())
        blob = json.dumps(out)
        self.assertEqual(out["respuesta"], NO_SE)
        self.assertNotIn("super-secret-token", blob)
        self.assertNotIn("RuntimeError", blob)


class TestEndpoint(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = TemporaryDirectory()
        cls.mem = Path(cls.tmp.name) / "mem.json"
        cls.listo = threading.Event()
        cls.caja = {}

        def hilo():
            cls.caja["httpd"] = _Servidor(LocalEngine(), cls.mem, 0)
            cls.listo.set()
            cls.caja["httpd"].serve_forever()

        cls.hilo = threading.Thread(target=hilo, daemon=True)
        cls.hilo.start()
        cls.listo.wait(30)
        cls.base = "http://127.0.0.1:%d" % cls.caja["httpd"].server_address[1]

    @classmethod
    def tearDownClass(cls):
        cls.caja["httpd"].shutdown()
        cls.caja["httpd"].server_close()
        cls.tmp.cleanup()

    def _abrir(self, path, data=None):
        req = urllib.request.Request(self.base + path, data=data, method="POST" if data is not None else "GET")
        if data is not None:
            req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status, resp.headers.get("Content-Type"), resp.read().decode("utf-8")

    def test_get_es_la_pantalla(self):
        status, ctype, html = self._abrir("/")
        self.assertEqual(status, 200)
        self.assertIn("text/html", ctype)
        self.assertIn("¿Qué productos me dan la plata?", html)
        self.assertIn("¿Me alcanza este mes?", html)
        self.assertIn("¿Cómo me fue con lo de la Coca?", html)
        self.assertIn("¿Cuánto deja la carne molida?", html)
        self.assertIn("Datos de ejemplo", html)
        self.assertNotIn("answer.json", html)

    def test_post_devuelve_la_prueba(self):
        cuerpo = json.dumps({"pregunta": "¿Qué productos me dan la plata?"}).encode()
        status, ctype, texto = self._abrir("/api/pregunta", cuerpo)
        self.assertEqual(status, 200)
        self.assertIn("application/json", ctype)
        out = json.loads(texto)
        self.assertEqual(out["sello"], "confirmado")
        self.assertTrue(out["pruebas"][0]["fuentes"])
        self.assertNotIn("answer.json", texto)

    def test_json_malo_es_no_se(self):
        status, _ctype, texto = self._abrir("/api/pregunta", b"no-es-json")
        self.assertEqual(status, 200)
        out = json.loads(texto)
        self.assertEqual(out["sello"], "no_se")
        self.assertNotIn("Traceback", texto)

    def test_ruta_desconocida(self):
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            self._abrir("/answer.json")
        self.assertEqual(ctx.exception.code, 404)
