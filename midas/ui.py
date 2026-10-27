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
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MIDAZ</title>
<style>
  :root {
    --bg: #101114;
    --card: #18181b;
    --ink: #f4f4f5;
    --muted: #a1a1aa;
    --line: rgba(255, 255, 255, 0.08);
    --gold: #D4AF37;
    --gold-dim: rgba(212, 175, 55, 0.16);
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; }
  body {
    min-height: 100vh;
    color: var(--ink);
    background: var(--bg);
    font-family: Inter, -apple-system, "Segoe UI", sans-serif;
    font-size: 17px;
    line-height: 1.5;
    -webkit-font-smoothing: antialiased;
  }
  ::selection { background: rgba(212, 175, 55, 0.35); }
  .wrap { max-width: 760px; margin: 0 auto; padding: 56px 24px 88px; }
  header { display: flex; justify-content: space-between; align-items: flex-end; gap: 16px; }
  h1 {
    margin: 0;
    font-size: 0.82rem;
    font-weight: 650;
    letter-spacing: 0.28em;
  }
  .tagline {
    margin: 10px 0 0;
    color: var(--gold);
    font-size: 1.35rem;
    font-weight: 560;
    letter-spacing: -0.02em;
  }
  .meta { display: flex; gap: 8px; flex-wrap: wrap; justify-content: flex-end; }
  .pill {
    border: 1px solid var(--line);
    color: var(--muted);
    border-radius: 999px;
    padding: 5px 11px;
    font-size: 0.78rem;
    letter-spacing: 0.04em;
  }
  .pill:empty { display: none; }
  form { margin-top: 44px; }
  label {
    display: block;
    margin-bottom: 8px;
    color: var(--muted);
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
  }
  .row { display: flex; gap: 10px; }
  input[type="text"] {
    flex: 1;
    min-width: 0;
    font: inherit;
    font-size: 1.05rem;
    color: var(--ink);
    background: #121316;
    border: 1px solid var(--line);
    border-radius: 14px;
    padding: 14px 16px;
  }
  input::placeholder { color: #71717a; }
  input:focus, button:focus-visible {
    outline: 2px solid rgba(212, 175, 55, 0.55);
    outline-offset: 2px;
  }
  button.ask {
    font: inherit;
    font-size: 1rem;
    font-weight: 650;
    color: #1c1404;
    background: var(--gold);
    border: 0;
    border-radius: 14px;
    padding: 0 22px;
    cursor: pointer;
  }
  button.ask:hover { filter: brightness(1.06); }
  button.ask:disabled { opacity: 0.55; cursor: progress; }
  .chips { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; }
  button.chip {
    font: inherit;
    font-size: 0.92rem;
    color: var(--ink);
    text-align: left;
    cursor: pointer;
    background: transparent;
    border: 1px solid var(--line);
    border-radius: 999px;
    padding: 8px 14px;
  }
  button.chip:hover, button.chip.activa { border-color: var(--gold); color: var(--gold); }
  .card {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: center;
    gap: 22px;
    margin-top: 36px;
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 22px;
    padding: 36px 28px;
    text-align: center;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
  }
  .answer {
    flex: 1 1 auto;
    min-width: 0;
    margin: 0;
    font-size: clamp(1.65rem, 3.1vw, 2.15rem);
    font-weight: 520;
    line-height: 1.35;
    letter-spacing: -0.025em;
  }
  .num.key {
    color: var(--gold);
    font-weight: 680;
    font-size: 1.22em;
    letter-spacing: -0.03em;
  }
  .seal {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    border-radius: 999px;
    padding: 6px 12px;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    white-space: nowrap;
  }
  .card > .seal { flex: 0 0 auto; }
  .seal::before {
    content: "";
    width: 0.45rem;
    height: 0.45rem;
    border-radius: 50%;
    background: currentColor;
  }
  .seal.confirmado { color: var(--gold); background: var(--gold-dim); border: 1px solid rgba(212, 175, 55, 0.45); }
  .seal.no_se { color: var(--muted); background: transparent; border: 1px solid var(--line); }
  .proof-wrap { margin-top: 22px; text-align: center; }
  button.proof-btn {
    font: inherit;
    font-size: 0.95rem;
    color: var(--ink);
    background: transparent;
    border: 1px solid rgba(255, 255, 255, 0.14);
    border-radius: 999px;
    padding: 10px 18px;
    cursor: pointer;
  }
  button.proof-btn:hover { border-color: var(--gold); color: var(--gold); }
  #proof { margin-top: 18px; text-align: left; }
  .receipt, .memoria {
    background: #141416;
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 18px 18px 16px;
    margin-bottom: 12px;
  }
  .receipt-head { display: flex; justify-content: space-between; gap: 12px; align-items: flex-start; }
  .receipt-title { margin: 0; font-size: 1.05rem; font-weight: 620; letter-spacing: -0.01em; }
  .file { margin: 4px 0 0; color: var(--muted); font-size: 0.82rem; }
  h3.kicker, h2 {
    margin: 18px 0 8px;
    font-size: 0.72rem;
    font-weight: 650;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--muted);
  }
  .memoria h2 { margin-top: 0; }
  .hint, .empty, .count { color: var(--muted); font-size: 0.92rem; margin: 0; }
  .count { margin-top: 8px; }
  .sources { display: flex; flex-wrap: wrap; gap: 6px; }
  .source {
    background: #222226;
    border-radius: 999px;
    padding: 4px 10px;
    font-size: 0.88rem;
    color: #e4e4e7;
  }
  pre {
    margin: 0;
    max-height: 16rem;
    overflow: auto;
    background: #0c0c0e;
    color: #e7e5e4;
    border-radius: 12px;
    padding: 14px 14px;
    font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
    font-size: 0.82rem;
    line-height: 1.45;
    white-space: pre-wrap;
  }
  .table-wrap { overflow-x: auto; }
  table { border-collapse: collapse; width: 100%; font-size: 0.92rem; }
  th, td { text-align: left; padding: 7px 10px; border-bottom: 1px solid var(--line); white-space: nowrap; }
  th { color: var(--muted); font-weight: 600; font-size: 0.75rem; letter-spacing: 0.04em; }
  .recall { border-top: 1px solid var(--line); padding-top: 10px; margin-top: 10px; }
  .recall:first-child { border-top: 0; padding-top: 0; margin-top: 0; }
  .recall p { margin: 0 0 4px; font-size: 0.98rem; line-height: 1.4; }
  .recall small { color: var(--muted); }
  .card.arrive { animation: arrive 0.45s ease; }
  @keyframes arrive {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: none; }
  }
  @media (prefers-reduced-motion: reduce) {
    .card.arrive { animation: none; }
  }
  @media (max-width: 640px) {
    .wrap { padding: 32px 16px 56px; }
    .row { flex-direction: column; }
    button.ask { height: 46px; }
    .card { flex-direction: column; padding: 28px 18px; }
    header { flex-direction: column; align-items: flex-start; }
  }
</style>
</head>
<body>
  <div class="wrap">
    <header>
      <div>
        <h1>MIDAZ</h1>
        <p class="tagline">Turn your data into gold.</p>
      </div>
      <div class="meta">
        <span class="pill" id="muestra" hidden>Sample data</span>
        <span class="pill" id="motor"></span>
      </div>
    </header>
    <form id="forma">
      <label for="pregunta">Question</label>
      <div class="row">
        <input id="pregunta" type="text" autocomplete="off" placeholder="Ask about sales, costs, or a past decision">
        <button class="ask" type="submit">Ask</button>
      </div>
    </form>
    <div class="chips" id="chips"></div>
    <article class="card" id="card" aria-live="polite">
      <p class="answer" id="respuesta">Looking at the data…</p>
      <p class="seal" id="sello" hidden></p>
    </article>
    <div class="proof-wrap">
      <button type="button" class="proof-btn" id="proof-btn" aria-expanded="false" aria-controls="proof">Show proof</button>
      <div id="proof" hidden>
        <div id="pruebas"></div>
        <section class="memoria">
          <h2>Memory</h2>
          <div id="memoria"></div>
        </section>
      </div>
    </div>
  </div>
  <script id="estado" type="application/json">__ESTADO__</script>
  <script>
    const estado = JSON.parse(document.getElementById("estado").textContent);
    const input = document.getElementById("pregunta");
    const respuesta = document.getElementById("respuesta");
    const sello = document.getElementById("sello");
    const card = document.getElementById("card");
    const pruebas = document.getElementById("pruebas");
    const memoria = document.getElementById("memoria");
    const proof = document.getElementById("proof");
    const proofBtn = document.getElementById("proof-btn");
    const askBtn = document.querySelector("button.ask");
    const NO_SE_ES = "No sé: no pude confirmar este dato con los datos.";
    const NO_SE_EN = "I don't know: I could not confirm this with the data.";
    const LABELS = {
      "¿Qué productos me dan la plata?": "Which products make me money?",
      "¿Me alcanza este mes?": "Can I cover this month?",
      "¿Cómo me fue con lo de la Coca?": "How did the Coke decision go?"
    };
    const TO_API = {};
    Object.keys(LABELS).forEach(function (k) { TO_API[LABELS[k]] = k; });
    const TITULOS = {
      "Los que más dejan": "Highest profit",
      "Para llegar al 80 %": "To reach 80%",
      "Ranking por ganancia": "Ranked by profit",
      "Vende mucho, deja poco": "High sales, low profit",
      "Mes contra gastos": "Month versus expenses",
      "Productos sin costo": "Products with no cost",
      "Antes y después": "Before and after",
      "Recibo": "Receipt"
    };
    const COLS = {
      n_productos: "Products",
      ganancia_total: "Profit",
      n_top20: "Top 20%",
      pct_top20: "% profit",
      n_para_80: "To reach 80%",
      pct_catalogo_para_80: "% of catalog",
      rank_ganancia: "Profit rank",
      rank_volumen: "Unit rank",
      product_id: "Code",
      name: "Product",
      category: "Category",
      unidades: "Units",
      ventas_sin_iva: "Sales ex-VAT",
      ganancia_bruta: "Profit",
      pct_ganancia: "% profit",
      pct_acumulado: "% cumulative",
      producto_estrella: "Star",
      brecha: "Gap",
      margen_pct: "Margin %",
      mes: "Month",
      costo_operativo: "Expenses",
      faltante: "Shortfall",
      ventas_sin_costo: "Sales with no cost",
      periodo: "Period",
      dias: "Days"
    };
    const ORIGEN = { POS: "POS", Inventario: "Inventory", Finanzas: "Finance" };
    let busy = false;

    if (estado.motor === "Zetaris") {
      document.getElementById("muestra").remove();
      document.getElementById("motor").textContent = "Zetaris";
    } else {
      const muestra = document.getElementById("muestra");
      muestra.hidden = false;
      muestra.textContent = "Sample data";
      document.getElementById("motor").textContent = "Local";
    }

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
    function textoVisible(t) {
      const s = (t || "").trim();
      if (!s || s === NO_SE_ES) return NO_SE_EN;
      return t;
    }
    function selloNombre(valor) { return valor === "confirmado" ? "Verified" : "Not verified"; }
    function ponerSello(node, valor) {
      node.hidden = false;
      node.className = "seal " + (valor === "confirmado" ? "confirmado" : "no_se");
      node.textContent = selloNombre(valor);
    }
    function alApi(texto) {
      const t = (texto || "").trim();
      return TO_API[t] || t;
    }
    function cerrarPrueba() {
      proof.hidden = true;
      proofBtn.setAttribute("aria-expanded", "false");
      proofBtn.textContent = "Show proof";
    }
    function setBusy(on) {
      busy = on;
      askBtn.disabled = on;
      askBtn.textContent = on ? "Asking…" : "Ask";
      askBtn.setAttribute("aria-busy", on ? "true" : "false");
    }
    function pintarRespuesta(texto) {
      const raw = textoVisible(texto);
      respuesta.replaceChildren();
      const re = /₡?\\d+(?:\\.\\d+)*\\s*%?/g;
      const matches = [];
      let found;
      while ((found = re.exec(raw)) !== null) matches.push(found);
      let keyIndex = -1;
      for (let i = 0; i < matches.length; i++) {
        if (/\\d\\.\\d+\\s*%/.test(matches[i][0])) { keyIndex = i; break; }
      }
      if (keyIndex < 0) {
        for (let i = 0; i < matches.length; i++) {
          if (/%/.test(matches[i][0])) { keyIndex = i; break; }
        }
      }
      let last = 0;
      matches.forEach(function (match, i) {
        if (match.index > last) respuesta.appendChild(document.createTextNode(raw.slice(last, match.index)));
        const span = document.createElement("span");
        if (i === keyIndex) span.className = "num key";
        span.textContent = match[0];
        respuesta.appendChild(span);
        last = match.index + match[0].length;
      });
      if (last < raw.length) respuesta.appendChild(document.createTextNode(raw.slice(last)));
    }
    function pintarMemoria(lista) {
      memoria.replaceChildren();
      if (!lista || !lista.length) {
        memoria.appendChild(el("p", "empty", "No decision saved yet."));
        return;
      }
      for (const m of lista) {
        const box = el("div", "recall");
        box.appendChild(el("p", null, m.texto || ""));
        if (m.detalle) box.appendChild(el("small", null, m.detalle));
        memoria.appendChild(box);
      }
    }
    function pintar(data) {
      pintarRespuesta(data.respuesta);
      ponerSello(sello, data.sello);
      card.classList.toggle("has-seal", true);
      pintarMemoria(data.memoria || estado.memoria);
      pruebas.replaceChildren();
      const lista = data.pruebas || [];
      const apiPregunta = data.pregunta || "";
      document.querySelectorAll("button.chip").forEach(function (b) {
        b.classList.toggle("activa", b.dataset.pregunta === apiPregunta);
      });
      if (!lista.length) {
        pruebas.appendChild(el("p", "empty", "No receipt for this answer."));
      }
      for (const p of lista) {
        const box = el("article", "receipt");
        const head = el("div", "receipt-head");
        const tit = el("div");
        tit.appendChild(el("h3", "receipt-title", TITULOS[p.titulo] || p.titulo || "Receipt"));
        if (p.id) tit.appendChild(el("p", "file", p.id));
        if (p.archivo) tit.appendChild(el("p", "file", p.archivo));
        head.appendChild(tit);
        const mini = el("span");
        ponerSello(mini, p.sello);
        head.appendChild(mini);
        box.appendChild(head);

        box.appendChild(el("h3", "kicker", "Sources"));
        const fuentes = el("div", "sources");
        const listaFuentes = p.fuentes || [];
        if (!listaFuentes.length) fuentes.appendChild(el("p", "empty", "No source in this receipt."));
        for (const f of listaFuentes) {
          const nombre = (ORIGEN[f.origen] || f.origen || "") + " · " + (f.nombre || "");
          fuentes.appendChild(el("span", "source", nombre));
        }
        box.appendChild(fuentes);

        box.appendChild(el("h3", "kicker", "SQL"));
        box.appendChild(el("pre", null, p.sql || ""));

        box.appendChild(el("h3", "kicker", "Data"));
        const filas = p.filas || [];
        if (!filas.length) {
          box.appendChild(el("p", "empty", "No rows."));
        } else {
          const wrap = el("div", "table-wrap");
          const table = document.createElement("table");
          const thead = document.createElement("thead");
          const hr = document.createElement("tr");
          (p.columnas || []).forEach(function (c, i) {
            const etiqueta = COLS[c] || (p.etiquetas || [])[i] || c;
            hr.appendChild(el("th", null, etiqueta));
          });
          thead.appendChild(hr);
          const tb = document.createElement("tbody");
          filas.forEach(function (fila) {
            const tr = document.createElement("tr");
            fila.forEach(function (v, i) { tr.appendChild(el("td", null, fmt(v, (p.columnas || [])[i]))); });
            tb.appendChild(tr);
          });
          table.appendChild(thead);
          table.appendChild(tb);
          wrap.appendChild(table);
          box.appendChild(wrap);
          if ((p.filas_total || 0) > filas.length) {
            box.appendChild(el("p", "count", "Showing " + filas.length + " of " + p.filas_total + " rows."));
          }
        }

        box.appendChild(el("h3", "kicker", "Verifier"));
        const nota = p.sello === "confirmado"
          ? "The verifier re-ran this SQL and the numbers match."
          : "The verifier did not confirm this receipt.";
        box.appendChild(el("p", "hint", nota));
        pruebas.appendChild(box);
      }
      card.classList.remove("arrive");
      void card.offsetWidth;
      card.classList.add("arrive");
    }
    async function preguntar(texto) {
      const visible = (texto || "").trim();
      if (!visible || busy) return;
      const api = alApi(visible);
      input.value = LABELS[api] || visible;
      respuesta.textContent = "Looking at the data…";
      sello.hidden = true;
      card.classList.remove("has-seal");
      card.classList.remove("arrive");
      cerrarPrueba();
      setBusy(true);
      try {
        const r = await fetch("/api/pregunta", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ pregunta: api })
        });
        pintar(await r.json());
      } catch (e) {
        pintar({
          respuesta: NO_SE_EN,
          sello: "no_se",
          pruebas: [],
          memoria: estado.memoria
        });
      } finally {
        setBusy(false);
      }
    }
    proofBtn.addEventListener("click", function () {
      const open = proof.hidden;
      proof.hidden = !open;
      proofBtn.setAttribute("aria-expanded", open ? "true" : "false");
      proofBtn.textContent = open ? "Hide proof" : "Show proof";
    });
    const chips = document.getElementById("chips");
    (estado.ejemplos || []).slice(0, 3).forEach(function (ej) {
      const label = LABELS[ej.pregunta] || ej.pregunta;
      const b = el("button", "chip", label);
      b.type = "button";
      b.dataset.pregunta = ej.pregunta;
      b.addEventListener("click", function () { preguntar(label); });
      chips.appendChild(b);
    });
    document.getElementById("forma").addEventListener("submit", function (ev) {
      ev.preventDefault();
      preguntar(input.value);
    });
    pintarMemoria(estado.memoria);
    const q = new URLSearchParams(location.search).get("pregunta");
    if (q) preguntar(q);
    else if ((estado.ejemplos || [])[0]) preguntar(estado.ejemplos[0].pregunta);
    else respuesta.textContent = "Ask a question. The answer shows up here.";
  </script>
</body>
</html>
"""
