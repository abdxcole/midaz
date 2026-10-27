"""Motor local sustituto (SQLite, stdlib) + recibos + respuesta HU-02.

Carga las 3 fuentes en 3 esquemas separados (ATTACH pos / inventario / finanzas),
corre los mismos archivos de sql/ que se mandaran a Zetaris, y arma un recibo
(receipt/receipt.schema.json) por cada frase con numero.
"""
from __future__ import annotations

import csv
import datetime as dt
import os
import re
import sqlite3
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SQL_DIR = ROOT / "sql"
DATA_DIR = ROOT / "data" / "output"

# esquema -> (tabla, archivo, columnas con tipo)
SOURCES = {
    "pos": ("ventas_pos", "ventas_pos.csv",
            [("date", "TEXT"), ("ticket", "TEXT"), ("product_id", "TEXT"),
             ("qty", "INTEGER"), ("unit_price_with_iva", "REAL")]),
    "inventario": ("costos_inventario", "costos_inventario.csv",
                   [("product_id", "TEXT"), ("name", "TEXT"), ("category", "TEXT"),
                    ("unit_cost", "REAL"), ("stock", "INTEGER")]),
    "finanzas": ("gastos_operativos", "gastos_operativos.csv",
                 [("month", "TEXT"), ("concept", "TEXT"), ("amount", "REAL")]),
}

BUSINESS_TERMS = {
    "precio_sin_iva": "unit_price_with_iva / 1.13",
    "ganancia_bruta": "qty * (unit_price_with_iva / 1.13 - unit_cost)",
    "margen": "ganancia_bruta / ventas_sin_iva, con ventas_sin_iva = qty * unit_price_with_iva / 1.13",
    "costo_operativo": "SUM(gastos_operativos.amount) del mes",
    "producto_estrella": "rank_ganancia <= FLOOR(0.2 * N), N = productos con costo y ventas",
    "sin_costo": "producto con ventas y sin fila en costos_inventario; no entra al 80/20",
}

VIEW_FILE = "00_margen_por_producto.sql"


# Federacion verificada en vivo (sql/zetaris/01_federar_fuentes.sql, opcion A), 12/12 el 2026-10-26.
ZETARIS_DEFAULT_SCHEMA_MAP = "pos=midaz_pos,inventario=midaz_inventario,finanzas=midaz_finanzas"


def load_sql(name: str) -> str:
    """Lee sql/<name> sin el ';' final. MIDAZ_SCHEMA_MAP='pos=a.b,inventario=c.d' reescribe prefijos."""
    sql = (SQL_DIR / name).read_text(encoding="utf-8").strip().rstrip(";").strip()
    mapping = os.environ.get("MIDAZ_SCHEMA_MAP") or (
        ZETARIS_DEFAULT_SCHEMA_MAP if os.environ.get("MIDAZ_ENGINE") == "zetaris" else "")
    for pair in filter(None, (p.strip() for p in mapping.split(","))):
        src, dst = pair.split("=", 1)
        sql = re.sub(rf"\b{re.escape(src.strip())}\.", dst.strip() + ".", sql)
    return sql


def sources_of(sql: str) -> list[dict]:
    out = []
    for schema, (table, fname, cols) in SOURCES.items():
        if f"{schema}.{table}" in sql:
            used = [c for c, _ in cols if re.search(rf"\b{c}\b", sql)]
            out.append({"schema": schema, "table": table, "file": f"data/output/{fname}", "columns": used})
    return out


class LocalEngine:
    name = "sqlite-local-standin"

    def __init__(self, data_dir: Path = DATA_DIR):
        self.con = sqlite3.connect(":memory:")
        for schema, (table, fname, cols) in SOURCES.items():
            self.con.execute(f"ATTACH DATABASE ':memory:' AS {schema}")
            self.con.execute(f"CREATE TABLE {schema}.{table} ({', '.join(f'{c} {t}' for c, t in cols)})")
            with open(data_dir / fname, newline="", encoding="utf-8") as f:
                rows = [[r[c] if r[c] != "" else None for c, _ in cols] for r in csv.DictReader(f)]
            self.con.executemany(
                f"INSERT INTO {schema}.{table} VALUES ({', '.join('?' * len(cols))})", rows)
        view = load_sql(VIEW_FILE)
        # SQLite: una vista que cruza bases adjuntas tiene que ser TEMP
        self.con.execute(re.sub(r"^\s*CREATE VIEW", "CREATE TEMP VIEW", view, flags=re.M))

    def run(self, sql: str) -> tuple[list[str], list[tuple], float]:
        t0 = time.perf_counter()
        cur = self.con.execute(sql)
        rows = cur.fetchall()
        ms = (time.perf_counter() - t0) * 1000
        return [d[0] for d in cur.description], rows, ms


PARAM_RE = {"product_id": r"P\d{3}", "fecha": r"\d{4}-\d{2}-\d{2}", "desde": r"\d{4}-\d{2}-\d{2}",
            "hasta": r"\d{4}-\d{2}-\d{2}", "dias": r"\d{1,3}"}


def fill_params(sql: str, params: dict | None) -> str:
    """Sustituye {{param}} con valores validados por regex (REST de Zetaris no tiene binding)."""
    params = dict(params or {})
    if "fecha" in params and "desde" not in params:
        d0 = dt.date.fromisoformat(params["fecha"])
        n = int(params.get("dias", 30))
        params.update(dias=str(n), desde=str(d0 - dt.timedelta(days=n)), hasta=str(d0 + dt.timedelta(days=n)))
    for k, v in params.items():
        if k not in PARAM_RE or not re.fullmatch(PARAM_RE[k], str(v)):
            raise ValueError(f"parametro invalido {k}={v!r}")
        sql = sql.replace("{{" + k + "}}", str(v))
    if "{{" in sql:
        faltan = re.findall(r"{{(\w+)}}", sql)
        raise ValueError(f"faltan parametros: {faltan}")
    return sql


def inline_view(sql: str, view_sql: str | None = None) -> str:
    """Pone la vista margen_por_producto como CTE delante de la consulta (Zetaris sin CREATE VIEW)."""
    if "margen_por_producto" not in sql:
        return sql
    body = re.sub(r"^\s*CREATE VIEW\s+margen_por_producto\s+AS\s*", "", view_sql or load_sql(VIEW_FILE),
                  flags=re.I | re.M)
    body = "\n".join(l for l in body.splitlines() if not l.strip().startswith("--"))
    sql = "\n".join(l for l in sql.splitlines() if not l.strip().startswith("--"))
    m = re.match(r"\s*WITH\s+", sql, flags=re.I)
    if m:
        return f"WITH margen_por_producto AS (\n{body}\n),\n" + sql[m.end():]
    return f"WITH margen_por_producto AS (\n{body}\n)\n{sql}"


def to_value(v):
    """REST de Zetaris manda todo como string (a veces en notacion exponencial): convertir antes de comparar."""
    if not isinstance(v, str):
        return v
    s = v.strip()
    if re.fullmatch(r"[+-]?\d+", s):
        return int(s)
    if re.fullmatch(r"[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?", s):
        f = float(s)
        return int(f) if f.is_integer() and "." not in s and "e" not in s.lower() else f
    return v


def _split_top(s: str, sep: str = ",") -> list[str]:
    out, depth, cur, q = [], 0, "", None
    for ch in s:
        if q:
            q = None if ch == q else q
        elif ch in "'\"`":
            q = ch
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif ch == sep and depth == 0:
            out.append(cur)
            cur = ""
            continue
        cur += ch
    return out + [cur]


def select_aliases(sql: str) -> list[str]:
    """Nombres de columnas del SELECT exterior (alias tras AS o ultimo identificador).
    Para respuestas Zetaris sin encabezados (p. ej. `SELECT 1 AS one` -> [["1"]])."""
    sql = re.sub(r"--[^\n]*", "", sql)
    masked, depth = [], 0  # enmascara lo que esta entre parentesis para hallar el SELECT exterior
    for ch in sql:
        depth += ch == "("
        masked.append(ch if depth == 0 else " ")
        depth -= ch == ")"
    m = "".join(masked)
    sel = [x.end() for x in re.finditer(r"\bSELECT\b(\s+DISTINCT\b)?", m, re.I)]
    if not sel:
        raise ValueError("no encuentro el SELECT exterior para nombrar columnas")
    start = sel[0]  # con UNION mandan los nombres del primer SELECT
    fr = re.compile(r"\b(FROM|WHERE|GROUP|ORDER|LIMIT|HAVING|UNION|WINDOW)\b", re.I).search(m, start)
    cols = []
    for item in _split_top(sql[start:fr.start() if fr else len(sql)]):
        item = item.strip()
        if item.endswith("*"):
            raise ValueError("SELECT * sin encabezados: no puedo nombrar columnas")
        a = re.search(r"(?:\bAS\s+)?[\"`]?([A-Za-z_][\w]*)[\"`]?\s*$", item, re.I)
        cols.append(a.group(1) if a else item)
    return cols


def parse_zetaris_data(data, sql: str | None = None) -> tuple[list[str], list[tuple]]:
    """Acepta las formas posibles de `data` (sin verificar cual usa Zetaris):
    {columns|schema|headers, rows|data|records} | lista de dicts | lista de listas con columns aparte."""
    cols, rows = None, None
    if isinstance(data, dict):
        for k in ("columns", "schema", "headers", "columnNames", "fields"):
            if k in data:
                cols = [c if isinstance(c, str) else (c.get("name") or c.get("columnName")) for c in data[k]]
                break
        for k in ("rows", "data", "records", "result", "results"):
            if k in data and isinstance(data[k], list):
                rows = data[k]
                break
        if rows is None and cols is None:
            for v in data.values():
                if isinstance(v, (dict, list)):
                    return parse_zetaris_data(v)
    elif isinstance(data, list):
        rows = data
    rows = rows or []
    if rows and isinstance(rows[0], dict):
        cols = cols or list(rows[0].keys())
        rows = [[r.get(c) for c in cols] for r in rows]
    if cols is None and sql and (not rows or isinstance(rows[0], (list, tuple))):
        cols = select_aliases(sql)  # filas como listas de texto sin encabezados (confirmado por Zetaris)
        if rows and len(rows[0]) != len(cols):
            raise ValueError(f"Zetaris mando {len(rows[0])} columnas y el SELECT nombra {len(cols)}: {cols}")
    if cols is None:
        raise ValueError(f"no reconozco la forma de la respuesta Zetaris: {str(data)[:200]}")
    return cols, [tuple(to_value(v) for v in r) for r in rows]


class ZetarisEngine:
    """Motor Zetaris por REST (HU-04). Las 3 fuentes se federan en Zetaris (sql/zetaris/) y los
    prefijos pos./inventario./finanzas. se mapean con MIDAZ_SCHEMA_MAP.
    MIDAZ_ZETARIS_VIEW=cte (por defecto) pone la vista como CTE; =view usa una vista creada en Zetaris."""
    name = "zetaris"

    def __init__(self, run_sql=None, view_mode: str | None = None):
        if run_sql is None:
            from .zetaris_client import run_sql
        self._run_sql = run_sql
        self.view_mode = view_mode or os.environ.get("MIDAZ_ZETARIS_VIEW", "cte")

    def run(self, sql: str) -> tuple[list[str], list[tuple], float]:
        if self.view_mode == "cte":
            sql = inline_view(sql)
        data, ms = self._run_sql(sql)
        cols, rows = parse_zetaris_data(data, sql)
        return cols, rows, ms


def make_engine(name: str | None = None):
    name = name or os.environ.get("MIDAZ_ENGINE", "local")
    if name == "zetaris":
        return ZetarisEngine()
    if name in ("local", "sqlite", LocalEngine.name):
        return LocalEngine()
    raise ValueError(f"motor desconocido: {name}")


def run_query(engine, name: str, params: dict | None = None) -> dict:
    sql = fill_params(load_sql(name), params)
    cols, rows, ms = engine.run(sql)
    return {"file": f"sql/{name}", "sql": sql, "columns": cols, "rows": rows, "ms": ms,
            "executed_at": dt.datetime.now().astimezone().isoformat(timespec="seconds")}


def dq_warnings(dq: dict) -> list[dict]:
    """Convierte el resultado de 01_calidad_datos.sql en advertencias del recibo."""
    out = []
    for chequeo, productos, unidades, ventas in dq["rows"]:
        if productos:
            out.append({"code": chequeo, "products": int(productos), "count": int(unidades or 0),
                        "detail": {"sin_costo": "productos con ventas y sin costo: excluidos del calculo",
                                   "precio_bajo_costo": "lineas vendidas por debajo del costo",
                                   "ventas_negativas": "lineas con cantidad o precio negativo"}[chequeo]})
    return out


def make_receipt(rid: str, claim: str, q: dict, warnings: list[dict], engine_name: str) -> dict:
    return {
        "id": rid,
        "claim": claim,
        "sql": q["sql"],
        "sql_file": q["file"],
        "view": {"name": "margen_por_producto", "definition_file": f"sql/{VIEW_FILE}",
                 "definition_sql": load_sql(VIEW_FILE), "business_terms": BUSINESS_TERMS},
        "sources": sources_of(q["sql"] + "\n" + load_sql(VIEW_FILE)),
        "row_count": len(q["rows"]),
        "executed_at": q["executed_at"],
        "execution_ms": round(q["ms"], 2),
        "engine": engine_name,
        "data_quality_warnings": warnings,
        "verifier": {"verdict": "pendiente", "by": None, "checked_at": None, "notes": None},
        "sample_data": True,
    }


def crc(x: float) -> str:
    return "\u20a1" + f"{x:,.0f}".replace(",", ".")


def build_answer(engine) -> dict:
    """Respuesta HU-02 (+ volumen vs ganancia + me alcanza) con un recibo por frase con numero."""
    dq = run_query(engine, "01_calidad_datos.sql")
    warnings = dq_warnings(dq)
    nocost = run_query(engine, "02_sin_costo_detalle.sql")
    res = run_query(engine, "11_hu02_8020_resumen.sql")
    rank = run_query(engine, "10_hu02_8020_ranking.sql")
    vol = run_query(engine, "20_vende_mucho_deja_poco.sql")
    mes = run_query(engine, "30_me_alcanza.sql")

    claims, receipts = [], []

    def add(rid, text, q):
        receipts.append(make_receipt(rid, text, q, warnings, engine.name))
        claims.append({"text": text, "receipt_id": rid, "has_number": bool(re.search(r"\d", text))})

    n_sin = len(nocost["rows"])
    if n_sin:
        add("R-NOSE", f"No s\u00e9: {n_sin} productos no tienen costo ({', '.join(r[0] for r in nocost['rows'])}); "
            f"vendieron {crc(sum(r[2] for r in nocost['rows']))} sin IVA y quedan fuera de este c\u00e1lculo.", nocost)

    n, total, ntop, pct_top, n80, pct80 = res["rows"][0]
    add("R-8020", f"De {n} productos con costo, el 20 % que m\u00e1s deja ({ntop} productos) hace el "
        f"{pct_top:.1f} % de su ganancia bruta ({crc(total)} en 90 d\u00edas, sin IVA).", res)
    add("R-80", f"Para llegar al 80 % de la ganancia hacen falta {n80} productos ({pct80:.1f} % del cat\u00e1logo).", res)
    top3 = ", ".join(r[3] for r in rank["rows"][:3])
    add("R-TOP", f"Los que m\u00e1s le dejan: {top3}.", rank)
    r1 = vol["rows"][0]
    add("R-VOL", f"{r1[4]} es el #{r1[0]} en unidades ({r1[5]:,}".replace(",", ".") + f") pero el #{r1[1]} en ganancia "
        f"(margen {r1[7]:.1f} %): vende mucho y deja poco.", vol)
    worst = max(mes["rows"], key=lambda r: r[3])
    if worst[3] > 0:
        add("R-MES", f"En {worst[0]} la ganancia bruta ({crc(worst[1])}) no cubri\u00f3 los gastos operativos "
            f"({crc(worst[2])}): faltaron {crc(worst[3])}.", mes)

    text = " ".join(c["text"] for c in claims)
    return {"question": "\u00bfQu\u00e9 productos me dan la plata?", "answer": text, "claims": claims,
            "receipts": receipts, "results": {"dq": dq, "resumen": res, "ranking": rank, "volumen": vol,
                                              "mes": mes, "sin_costo": nocost}}
