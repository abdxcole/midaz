"""Pantalla local de MIDAZ para el video del pitch. Solo presentación.

No calcula cifras: llama a build_answer, verify_answer, run_followup y al
verificador. La lógica de negocio sigue en core.py, verifier.py y memory.py.
"""
from __future__ import annotations

import json
import os
import re
import unicodedata
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

from midas.core import build_answer, make_receipt
from midas.memory import DecisionMemory
from midas.verifier import NO_SE, verify_answer, verify_receipt

MAX_FILAS = 5
MAX_PREGUNTA = 400
HOST = "127.0.0.1"

EJEMPLOS = [
    {"id": "plata", "pregunta": "¿Qué productos me dan la plata?"},
    {"id": "alcanza", "pregunta": "¿Me alcanza este mes?"},
    {"id": "coca", "pregunta": "¿Cómo me fue con lo de la Coca?"},
    {"id": "carne", "pregunta": "¿Cuánto deja la carne molida?"},
]

_RECIBOS = {
    "plata": ("R-8020", "R-TOP", "R-80", "R-NOSE"),
    "alcanza": ("R-MES",),
    "carne": ("R-NOSE",),
    "volumen": ("R-VOL",),
}

_MESES = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
          "septiembre", "setiembre", "octubre", "noviembre", "diciembre")

_TABLAS = {
    "ventas_pos": "POS",
    "costos_inventario": "Inventario",
    "gastos_operativos": "Finanzas",
}
_ORDEN_TABLA = {"ventas_pos": 0, "costos_inventario": 1, "gastos_operativos": 2}

_TITULOS = {
    "R-8020": "Los que más dejan",
    "R-80": "Para llegar al 80 %",
    "R-TOP": "Ranking por ganancia",
    "R-VOL": "Vende mucho, deja poco",
    "R-MES": "Mes contra gastos",
    "R-NOSE": "Productos sin costo",
    "R-SEG": "Antes y después",
}

_COLUMNAS = {
    "n_productos": "Productos",
    "ganancia_total": "Ganancia",
    "n_top20": "Top 20 %",
    "pct_top20": "% ganancia",
    "n_para_80": "Para el 80 %",
    "pct_catalogo_para_80": "% catálogo",
    "rank_ganancia": "# ganancia",
    "rank_volumen": "# unidades",
    "product_id": "Código",
    "name": "Producto",
    "category": "Categoría",
    "unidades": "Unidades",
    "ventas_sin_iva": "Ventas sin IVA",
    "ganancia_bruta": "Ganancia",
    "pct_ganancia": "% ganancia",
    "pct_acumulado": "% acumulado",
    "producto_estrella": "Estrella",
    "brecha": "Brecha",
    "margen_pct": "Margen %",
    "mes": "Mes",
    "costo_operativo": "Gastos",
    "faltante": "Faltante",
    "ventas_sin_costo": "Ventas sin costo",
    "periodo": "Periodo",
    "dias": "Días",
}

_BASE: dict[int, dict] = {}
_SECRETOS = ("api_key", "api-key", "token", "bearer", "secret", "password", "authorization")


def memoria_por_defecto() -> Path:
    from midas.memory import ROOT
    return ROOT / "out" / "hmem" / "ui_memoria.json"


def etiqueta_motor(engine) -> str:
    if getattr(engine, "name", "") == "zetaris":
        return "Zetaris"
    return "Local, sin Zetaris"


def _norm(texto: str) -> str:
    t = unicodedata.normalize("NFKD", texto.lower()).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def clasificar(pregunta: str) -> str:
    """Elige una respuesta que el motor ya sabe armar. Si no, no se inventa."""
    t = _norm(pregunta)
    if not t:
        return "vacia"
    if "coca" in t.split() or "como me fue" in t:
        return "seguimiento"
    if any(m in t.split() for m in _MESES):
        return "fuera"
    if "carne" in t.split() or "molida" in t.split() or "sin costo" in t:
        return "carne"
    if "vende mucho" in t or "deja poco" in t:
        return "volumen"
    if "alcanza" in t.split():
        return "alcanza"
    if "plata" in t.split() or "ganancia" in t.split() or re.search(r"\b80\b", t) or "8020" in t.split():
        return "plata"
    return "fuera"


def _sin_comentarios(sql: str) -> str:
    """Los comentarios del archivo nombran las tres fuentes aunque la consulta no las use."""
    return "\n".join(linea.split("--", 1)[0] for linea in (sql or "").splitlines())


def fuentes_visibles(recibo: dict) -> list[dict]:
    """Nombres de fuente y tabla tal como quedaron en el SQL (local o Zetaris)."""
    vista = recibo.get("view") or {}
    blob = _sin_comentarios(recibo.get("sql") or "") + "\n" + _sin_comentarios(vista.get("definition_sql") or "")
    vistos, out = set(), []
    for m in re.finditer(
            r"((?:[A-Za-z_][\w]*\.)+)(ventas_pos|costos_inventario|gastos_operativos)\b", blob):
        nombre = m.group(1) + m.group(2)
        if nombre.lower() in vistos:
            continue
        vistos.add(nombre.lower())
        tabla = m.group(2)
        out.append({"origen": _TABLAS[tabla], "nombre": nombre, "tabla": tabla})
    if not out:
        for src in recibo.get("sources") or []:
            tabla = src.get("table") or ""
            if tabla not in _TABLAS:
                continue
            esquema = src.get("schema") or ""
            nombre = f"{esquema}.{tabla}" if esquema else tabla
            if nombre.lower() in vistos:
                continue
            vistos.add(nombre.lower())
            out.append({"origen": _TABLAS[tabla], "nombre": nombre, "tabla": tabla})
    out.sort(key=lambda f: (_ORDEN_TABLA.get(f["tabla"], 9), f["nombre"]))
    return out


def _publico(texto) -> str:
    if not isinstance(texto, str):
        return ""
    bajo = texto.lower()
    if any(s in bajo for s in _SECRETOS):
        return ""
    return texto.strip()[:180]


def _celda(v):
    if v is None or isinstance(v, (str, bool, int)):
        return v
    if isinstance(v, float):
        if v != v or v in (float("inf"), float("-inf")):
            return None
        return v
    return str(v)[:80]


def _sello(veredicto: str) -> tuple[str, str]:
    if veredicto == "confirmado":
        return "confirmado", "Confirmado"
    return "no_se", "No sé"


def armar_prueba(recibo: dict, columnas, filas) -> dict:
    sello, texto = _sello((recibo.get("verifier") or {}).get("verdict"))
    cols = [str(c) for c in (columnas or [])]
    filas = list(filas or [])
    return {
        "id": recibo.get("id") or "",
        "titulo": _TITULOS.get(recibo.get("id") or "", "Recibo"),
        "sql": recibo.get("sql") or "",
        "archivo": recibo.get("sql_file") or "",
        "fuentes": fuentes_visibles(recibo),
        "columnas": cols,
        "etiquetas": [_COLUMNAS.get(c, c) for c in cols],
        "filas": [[_celda(v) for v in row] for row in filas[:MAX_FILAS]],
        "filas_total": len(filas),
        "sello": sello,
        "sello_texto": texto,
    }


def _no_se(pregunta: str, motor: str, memoria: list | None = None) -> dict:
    return {
        "pregunta": pregunta,
        "respuesta": NO_SE,
        "sello": "no_se",
        "sello_texto": "No sé",
        "muestra": True,
        "motor": motor,
        "pruebas": [],
        "memoria": memoria or [],
    }


def _base(engine) -> dict:
    clave = id(engine)
    if clave not in _BASE:
        ans = build_answer(engine)
        verify_answer(engine, ans)
        _BASE[clave] = ans
    return _BASE[clave]


def _filas_de(ans: dict, archivo: str):
    for q in ans.get("results", {}).values():
        if q.get("file") == archivo:
            return q.get("columns") or [], q.get("rows") or []
    return [], []


def listar_memoria(mem: DecisionMemory) -> list[dict]:
    out = []
    for rec in mem.hm.store.all():
        if "decision" not in (rec.get("tags") or []):
            continue
        prov = rec.get("provenance") or {}
        out.append({"id": rec.get("id") or "", "texto": _publico(rec.get("content")),
                    "detalle": _publico(prov.get("label"))})
    return out


def asegurar_memoria(mem_path) -> DecisionMemory:
    import run
    mem = DecisionMemory(mem_path)
    if not any("decision" in (r.get("tags") or []) for r in mem.hm.store.all()):
        mem.remember(**run.DEMO_DECISION)
    return mem


def _frase_sql(respuesta: str) -> str:
    """answer_followup cita el recuerdo (fechas, ids) y después los números del SQL.

    El verificador solo puede confirmar la segunda parte: la primera trae cifras
    que no están en las filas (el 2.5 L, la fecha, el id del recuerdo).
    """
    marca = "): "
    i = respuesta.rfind(marca)
    frase = respuesta[i + len(marca):].strip() if i != -1 else respuesta.strip()
    if frase[:1].islower():
        frase = frase[:1].upper() + frase[1:]
    return frase


def _responder_seguimiento(engine, pregunta: str, mem_path, motor: str) -> dict:
    import run
    mem = asegurar_memoria(mem_path)
    f = run.run_followup(engine, pregunta, mem_path)
    memoria = listar_memoria(DecisionMemory(mem_path)) or listar_memoria(mem)
    if f.get("error") or not f.get("receipt"):
        return _no_se(pregunta, motor, memoria)
    frase = _frase_sql(f.get("answer") or "")
    if not frase:
        return _no_se(pregunta, motor, memoria)
    q = f["receipt"]
    recibo = make_receipt("R-SEG", frase, q, [], engine.name)
    recibo["verifier"] = verify_receipt(engine, recibo, q.get("rows"))
    prueba = armar_prueba(recibo, q.get("columns"), q.get("rows"))
    if prueba["sello"] != "confirmado":
        vista = _no_se(pregunta, motor, memoria)
        vista["pruebas"] = [prueba]
        return vista
    return {
        "pregunta": pregunta,
        "respuesta": frase,
        "sello": "confirmado",
        "sello_texto": "Confirmado",
        "muestra": True,
        "motor": motor,
        "pruebas": [prueba],
        "memoria": memoria,
    }


def _responder(engine, pregunta: str, mem_path) -> dict:
    pregunta = " ".join((pregunta or "").split())
    if len(pregunta) > MAX_PREGUNTA:
        pregunta = pregunta[:MAX_PREGUNTA].rstrip()
    motor = etiqueta_motor(engine)
    memoria = listar_memoria(asegurar_memoria(mem_path))
    kind = clasificar(pregunta)
    if kind == "vacia":
        return _no_se(pregunta, motor, memoria)
    if kind == "seguimiento":
        return _responder_seguimiento(engine, pregunta, mem_path, motor)
    if kind == "fuera":
        return _no_se(pregunta, motor, memoria)
    ans = _base(engine)
    ids = set(_RECIBOS[kind])
    orden = {rid: i for i, rid in enumerate(_RECIBOS[kind])}
    recibos = [r for r in ans["receipts"] if r["id"] in ids]
    recibos.sort(key=lambda r: orden.get(r["id"], 9))
    if not recibos:
        return _no_se(pregunta, motor, memoria)
    textos, pruebas, vistos = [], [], set()
    por_id = {c["receipt_id"]: c for c in ans["claims"]}
    sellos = []
    for r in recibos:
        c = por_id.get(r["id"])
        if c:
            textos.append(c["text"])
        cols, rows = _filas_de(ans, r.get("sql_file"))
        prueba = armar_prueba(r, cols, rows)
        sellos.append(prueba["sello"])
        archivo = r.get("sql_file") or r.get("id")
        if archivo in vistos:
            continue
        vistos.add(archivo)
        pruebas.append(prueba)
    sello = "confirmado" if sellos and all(s == "confirmado" for s in sellos) else "no_se"
    return {
        "pregunta": pregunta,
        "respuesta": " ".join(textos) if textos else NO_SE,
        "sello": sello,
        "sello_texto": "Confirmado" if sello == "confirmado" else "No sé",
        "muestra": True,
        "motor": motor,
        "pruebas": pruebas,
        "memoria": memoria,
    }


def responder(engine, pregunta: str, mem_path=None) -> dict:
    """JSON de la pantalla. Nunca incluye notas del motor, llaves ni answer.json."""
    path = Path(mem_path) if mem_path else memoria_por_defecto()
    try:
        return _responder(engine, pregunta if isinstance(pregunta, str) else "", path)
    except Exception:
        return _no_se(pregunta if isinstance(pregunta, str) else "", etiqueta_motor(engine))


def estado(engine, mem_path=None) -> dict:
    path = Path(mem_path) if mem_path else memoria_por_defecto()
    try:
        memoria = listar_memoria(asegurar_memoria(path))
    except Exception:
        memoria = []
    return {"ejemplos": EJEMPLOS, "motor": etiqueta_motor(engine), "muestra": True, "memoria": memoria}


def pagina(datos: dict) -> str:
    blob = json.dumps(datos, ensure_ascii=False).replace("<", "\\u003c")
    return _HTML.replace("__ESTADO__", blob)


class _Servidor(HTTPServer):
    """Un solo hilo: el motor local es SQLite y su conexión no cruza hilos."""
    def __init__(self, engine, mem_path, puerto: int):
        self.engine = engine
        self.mem_path = Path(mem_path)
        super().__init__((HOST, puerto), _Manejador)


class _Manejador(BaseHTTPRequestHandler):
    server: _Servidor

    def log_message(self, fmt, *args):
        return

    def do_GET(self):
        if urlparse(self.path).path != "/":
            self._texto(404, "No está.")
            return
        cuerpo = pagina(estado(self.server.engine, self.server.mem_path)).encode("utf-8")
        self._bytes(200, "text/html; charset=utf-8", cuerpo)

    def do_POST(self):
        if urlparse(self.path).path != "/api/pregunta":
            self._texto(404, "No está.")
            return
        try:
            n = int(self.headers.get("Content-Length") or "0")
        except ValueError:
            n = 0
        if n < 0 or n > 8000:
            self._json(200, _no_se("", etiqueta_motor(self.server.engine)))
            return
        crudo = self.rfile.read(n) if n else b""
        try:
            data = json.loads(crudo.decode("utf-8") or "{}")
            pregunta = data.get("pregunta") if isinstance(data, dict) else ""
        except (UnicodeDecodeError, json.JSONDecodeError, AttributeError):
            pregunta = ""
        if not isinstance(pregunta, str):
            pregunta = ""
        self._json(200, responder(self.server.engine, pregunta, self.server.mem_path))

    def _json(self, code: int, payload: dict):
        self._bytes(code, "application/json; charset=utf-8",
                    json.dumps(payload, ensure_ascii=False).encode("utf-8"))

    def _texto(self, code: int, texto: str):
        self._bytes(code, "text/plain; charset=utf-8", texto.encode("utf-8"))

    def _bytes(self, code: int, ctype: str, cuerpo: bytes):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(cuerpo)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(cuerpo)


def linea_arranque(engine, url: str) -> str:
    """«SAMPLE DATA» solo si el motor no es Zetaris."""
    if getattr(engine, "name", "") == "zetaris":
        return f"MIDAZ en {url}"
    return f"SAMPLE DATA — MIDAZ en {url}"


def servir(engine, puerto=None, mem_path=None) -> int:
    """Abre la pantalla en 127.0.0.1. Carga .env otra vez por si se llama directo."""
    import run
    run.cargar_env()
    if puerto is None:
        crudo = os.environ.get("MIDAZ_UI_PORT", "8765")
        try:
            puerto = int(crudo)
        except ValueError:
            print("MIDAZ_UI_PORT no es un puerto válido.", flush=True)
            return 1
    path = Path(mem_path) if mem_path else memoria_por_defecto()
    try:
        httpd = _Servidor(engine, path, puerto)
    except OSError:
        print(f"No pude abrir {HOST}:{puerto}.", flush=True)
        return 1
    url = f"http://{HOST}:{httpd.server_address[1]}"
    print(linea_arranque(engine, url), flush=True)
    print(f"Motor: {etiqueta_motor(engine)}. Ctrl+C para salir.", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nCerrado.", flush=True)
    finally:
        httpd.server_close()
    return 0


_HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MIDAZ</title>
<style>
  :root {
    --paper: #f3ecdf;
    --ink: #1c1814;
    --muted: #5e564c;
    --gold: #8a6430;
    --line: #e3d8c4;
    --card: #fffaf3;
    --green: #0c6b3c;
    --green-bg: #e6f6ec;
    --amber: #7a4e0b;
    --amber-bg: #f8f0dc;
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; }
  body {
    min-height: 100vh;
    color: var(--ink);
    background:
      radial-gradient(900px 420px at 8% -10%, rgba(196, 154, 74, 0.28), transparent 60%),
      var(--paper);
    font-family: "Segoe UI", system-ui, sans-serif;
  }
  .marco { max-width: 1180px; margin: 0 auto; padding: 28px 32px 48px; }
  header { display: flex; justify-content: space-between; align-items: flex-end; gap: 16px; }
  .logo { font-size: 1.35rem; letter-spacing: 0.18em; font-weight: 750; }
  .slogan { display: block; margin-top: 4px; color: var(--gold); font-size: 1.02rem; }
  .meta { display: flex; gap: 8px; flex-wrap: wrap; justify-content: flex-end; }
  .pastilla {
    border: 1px solid var(--line); background: var(--card); color: var(--muted);
    border-radius: 999px; padding: 6px 12px; font-size: 0.92rem;
  }
  .layout { display: grid; grid-template-columns: minmax(0, 1fr) 280px; gap: 22px; margin-top: 22px; }
  .pregunta label { display: block; font-size: 0.95rem; color: var(--muted); margin-bottom: 8px; }
  form { display: flex; gap: 10px; }
  input[type="text"] {
    flex: 1; font: inherit; font-size: 1.25rem; padding: 14px 16px;
    border-radius: 14px; border: 1.5px solid #d9cdb8; background: white; color: var(--ink);
  }
  input:focus, button:focus { outline: 3px solid rgba(138, 100, 48, 0.35); outline-offset: 1px; }
  button.ir {
    font: inherit; font-size: 1.1rem; font-weight: 650; color: white; background: #2a241c;
    border: 0; border-radius: 14px; padding: 0 20px; cursor: pointer;
  }
  button.ir:hover { background: #111; }
  .chips { display: flex; flex-wrap: wrap; gap: 8px; margin: 12px 0 8px; }
  button.chip {
    font: inherit; font-size: 1rem; text-align: left; cursor: pointer;
    background: var(--card); border: 1px solid var(--line); border-radius: 999px; padding: 8px 14px;
  }
  button.chip.activa, button.chip:hover { border-color: var(--gold); color: #5c4014; }
  .respuesta {
    font-family: Georgia, "Iowan Old Style", Palatino, serif;
    font-size: clamp(1.7rem, 2.5vw, 2.3rem);
    line-height: 1.32; margin: 18px 0 12px; min-height: 2.6em;
  }
  .sello {
    display: inline-flex; align-items: center; gap: 8px;
    border-radius: 999px; padding: 7px 14px; font-weight: 750;
    letter-spacing: 0.06em; text-transform: uppercase; font-size: 0.95rem;
  }
  .sello.confirmado { background: var(--green-bg); color: var(--green); border: 2px solid var(--green); }
  .sello.no_se { background: var(--amber-bg); color: var(--amber); border: 2px solid var(--amber); }
  .sello i { width: 0.7rem; height: 0.7rem; border-radius: 50%; background: currentColor; display: block; }
  h2 { font-size: 0.85rem; letter-spacing: 0.14em; text-transform: uppercase; color: var(--muted); margin: 26px 0 10px; }
  .pista { color: var(--muted); font-size: 1.05rem; margin: 0 0 8px; }
  .prueba {
    background: var(--card); border: 1px solid var(--line); border-radius: 16px;
    padding: 14px 16px 16px; margin-bottom: 12px;
  }
  .prueba header { display: flex; justify-content: space-between; gap: 12px; align-items: center; margin-bottom: 8px; }
  .prueba h3 { margin: 0; font-size: 1.15rem; }
  .archivo { color: var(--muted); font-size: 0.9rem; }
  .fuentes { display: flex; flex-wrap: wrap; gap: 6px; margin: 8px 0; }
  .fuente {
    background: #f6efe2; border-radius: 999px; padding: 4px 10px; font-size: 0.95rem; color: #3f3426;
  }
  pre {
    margin: 8px 0; max-height: 9.5rem; overflow: auto; background: #1c1814; color: #f6efe2;
    border-radius: 12px; padding: 12px 14px; font-size: 0.92rem; line-height: 1.4;
    white-space: pre-wrap;
  }
  .tabla { overflow-x: auto; }
  table { border-collapse: collapse; width: 100%; font-size: 1rem; }
  th, td { text-align: left; padding: 6px 10px; border-bottom: 1px solid var(--line); white-space: nowrap; }
  th { color: var(--muted); font-weight: 650; font-size: 0.85rem; }
  .cuenta { color: var(--muted); font-size: 0.9rem; margin: 6px 0 0; }
  aside {
    background: var(--card); border: 1px solid var(--line); border-radius: 16px;
    padding: 16px; align-self: start; position: sticky; top: 16px;
  }
  aside h2 { margin-top: 0; }
  .recuerdo { border-top: 1px solid var(--line); padding-top: 10px; margin-top: 10px; }
  .recuerdo p { margin: 0 0 6px; font-size: 1.05rem; line-height: 1.35; }
  .recuerdo small { color: var(--muted); }
  .vacio { color: var(--muted); }
  @media (max-width: 900px) {
    .layout { grid-template-columns: 1fr; }
    .marco { padding: 18px 16px 32px; }
    aside { position: static; }
  }
</style>
</head>
<body>
  <div class="marco">
    <header>
      <div>
        <div class="logo">MIDAZ</div>
        <span class="slogan">Turn your data into gold.</span>
      </div>
      <div class="meta">
        <span class="pastilla">Datos de ejemplo</span>
        <span class="pastilla" id="motor"></span>
      </div>
    </header>
    <div class="layout">
      <main>
        <div class="pregunta">
          <label for="pregunta">Pregunta de la pulpería</label>
          <form id="forma">
            <input id="pregunta" type="text" autocomplete="off" placeholder="Pregunte por las ventas, los costos o una decisión…">
            <button class="ir" type="submit">Preguntar</button>
          </form>
          <div class="chips" id="chips"></div>
        </div>
        <p class="respuesta" id="respuesta">Elija una pregunta. La respuesta queda en grande y la prueba, debajo.</p>
        <p id="sello" hidden></p>
        <h2>Prueba</h2>
        <p class="pista" id="pista">El SQL, las filas y el sello del verificador aparecen aquí.</p>
        <div id="pruebas"></div>
      </main>
      <aside>
        <h2>Memoria H-MEM</h2>
        <div id="memoria"></div>
      </aside>
    </div>
  </div>
  <script id="estado" type="application/json">__ESTADO__</script>
  <script>
    const estado = JSON.parse(document.getElementById("estado").textContent);
    const input = document.getElementById("pregunta");
    const respuesta = document.getElementById("respuesta");
    const sello = document.getElementById("sello");
    const pruebas = document.getElementById("pruebas");
    const pista = document.getElementById("pista");
    const memoria = document.getElementById("memoria");
    document.getElementById("motor").textContent = estado.motor === "Zetaris" ? "Motor Zetaris" : "Sin Zetaris";

    function el(tag, clase, texto) {
      const n = document.createElement(tag);
      if (clase) n.className = clase;
      if (texto != null) n.textContent = texto;
      return n;
    }
    function miles(n) {
      const neg = n < 0;
      const s = String(Math.abs(Math.round(n)));
      return (neg ? "-" : "") + s.replace(/\\B(?=(\\d{3})+(?!\\d))/g, ".");
    }
    function dinero(col) { return /ganancia|venta|costo|faltante|amount/i.test(col || ""); }
    function pct(col) { return /pct|margen/i.test(col || ""); }
    function fmt(v, col) {
      if (v === null || v === undefined || v === "") return "—";
      if (typeof v === "number" && Number.isFinite(v)) {
        if (dinero(col)) return "₡" + miles(v);
        if (Number.isInteger(v) || Math.abs(v - Math.round(v)) < 0.001) return miles(v);
        const t = v.toFixed(1).replace(".", ",");
        return pct(col) ? t + " %" : t;
      }
      return String(v);
    }
    function pintarMemoria(lista) {
      memoria.replaceChildren();
      if (!lista || !lista.length) {
        memoria.appendChild(el("p", "vacio", "Aún no hay una decisión guardada."));
        return;
      }
      for (const m of lista) {
        const box = el("div", "recuerdo");
        box.appendChild(el("p", null, m.texto || ""));
        if (m.detalle) box.appendChild(el("small", null, m.detalle));
        memoria.appendChild(box);
      }
    }
    function pintar(data) {
      respuesta.textContent = data.respuesta || "No sé: no pude confirmar este dato con los datos.";
      sello.hidden = false;
      sello.className = "sello " + (data.sello === "confirmado" ? "confirmado" : "no_se");
      sello.replaceChildren(el("i"), document.createTextNode(data.sello_texto || "No sé"));
      pintarMemoria(data.memoria || estado.memoria);
      pruebas.replaceChildren();
      const lista = data.pruebas || [];
      pista.hidden = lista.length > 0;
      document.querySelectorAll("button.chip").forEach((b) => {
        b.classList.toggle("activa", b.textContent === data.pregunta);
      });
      for (const p of lista) {
        const card = el("article", "prueba");
        const head = document.createElement("header");
        const tit = el("div");
        tit.appendChild(el("h3", null, p.titulo || "Recibo"));
        if (p.archivo) tit.appendChild(el("div", "archivo", p.archivo));
        head.appendChild(tit);
        const mini = el("span", "sello " + (p.sello === "confirmado" ? "confirmado" : "no_se"));
        mini.appendChild(el("i"));
        mini.appendChild(document.createTextNode(p.sello_texto || "No sé"));
        head.appendChild(mini);
        card.appendChild(head);
        const fuentes = el("div", "fuentes");
        for (const f of p.fuentes || []) fuentes.appendChild(el("span", "fuente", f.origen + " · " + f.nombre));
        card.appendChild(fuentes);
        card.appendChild(el("pre", null, p.sql || ""));
        const wrap = el("div", "tabla");
        const table = document.createElement("table");
        const thead = document.createElement("thead");
        const hr = document.createElement("tr");
        (p.etiquetas || []).forEach((c) => hr.appendChild(el("th", null, c)));
        thead.appendChild(hr);
        const tb = document.createElement("tbody");
        (p.filas || []).forEach((fila) => {
          const tr = document.createElement("tr");
          fila.forEach((v, i) => tr.appendChild(el("td", null, fmt(v, (p.columnas || [])[i]))));
          tb.appendChild(tr);
        });
        table.appendChild(thead);
        table.appendChild(tb);
        wrap.appendChild(table);
        card.appendChild(wrap);
        if ((p.filas_total || 0) > (p.filas || []).length) {
          card.appendChild(el("p", "cuenta", "Mostrando " + p.filas.length + " de " + p.filas_total + " filas."));
        }
        pruebas.appendChild(card);
      }
    }
    async function preguntar(texto) {
      texto = (texto || "").trim();
      if (!texto) return;
      input.value = texto;
      respuesta.textContent = "Revisando los datos…";
      sello.hidden = true;
      try {
        const r = await fetch("/api/pregunta", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ pregunta: texto })
        });
        pintar(await r.json());
      } catch (e) {
        pintar({
          respuesta: "No sé: no pude confirmar este dato con los datos.",
          sello: "no_se",
          sello_texto: "No sé",
          pruebas: [],
          memoria: estado.memoria
        });
      }
    }
    const chips = document.getElementById("chips");
    for (const ej of estado.ejemplos || []) {
      const b = el("button", "chip", ej.pregunta);
      b.type = "button";
      b.addEventListener("click", () => preguntar(ej.pregunta));
      chips.appendChild(b);
    }
    document.getElementById("forma").addEventListener("submit", (ev) => {
      ev.preventDefault();
      preguntar(input.value);
    });
    pintarMemoria(estado.memoria);
    const q = new URLSearchParams(location.search).get("pregunta");
    if (q) preguntar(q);
  </script>
</body>
</html>
"""
