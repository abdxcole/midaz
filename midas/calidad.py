"""Reglas de calidad de datos en codigo (HU-03 / HU-12), espejo de sql/01_calidad_datos.sql y
sql/02_sin_costo_detalle.sql. Corren sobre las filas crudas de las 3 fuentes, sin SQL, para que
el "No sé" se decida en codigo aunque el motor (SQLite o Zetaris) falle o devuelva otra cosa.

Reglas (codigo -> que dispara):
  sin_costo          producto con ventas y sin fila en costos_inventario      -> "No sé" (bloquea)
  precio_bajo_costo  linea vendida con precio sin IVA < costo unitario        -> advertencia
  ventas_negativas   linea con qty < 0 o precio < 0 (devoluciones)            -> advertencia
  costo_invalido     costo unitario vacio, <= 0 o no numerico                 -> advertencia (extra, sin SQL)
  fila_incompleta    venta sin fecha, producto, qty o precio validos          -> advertencia (extra, sin SQL)
Los casos finales los define ARGOS (#4); estas son las del Sprint 1 mas dos extra.
"""
from __future__ import annotations

import csv
from pathlib import Path

from .core import DATA_DIR, crc

IVA = 1.13
BLOQUEANTES = {"sin_costo"}


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def load_rows(data_dir: Path = DATA_DIR) -> tuple[list[dict], list[dict]]:
    with open(data_dir / "ventas_pos.csv", newline="", encoding="utf-8") as f:
        ventas = list(csv.DictReader(f))
    with open(data_dir / "costos_inventario.csv", newline="", encoding="utf-8") as f:
        costos = list(csv.DictReader(f))
    return ventas, costos


def evaluar(ventas: list[dict], costos: list[dict]) -> dict:
    """Devuelve {codigo: {"productos": [...], "lineas": n, "unidades": n, "ventas_sin_iva": x}}."""
    costo = {}
    invalidos = set()
    for c in costos:
        u = _f(c.get("unit_cost"))
        costo[c["product_id"]] = u
        if u is None or u <= 0:
            invalidos.add(c["product_id"])
    out = {k: {"productos": set(), "lineas": 0, "unidades": 0, "ventas_sin_iva": 0.0}
           for k in ("sin_costo", "precio_bajo_costo", "ventas_negativas", "costo_invalido", "fila_incompleta")}

    def hit(k, pid, qty=0, vsi=0.0):
        out[k]["productos"].add(pid)
        out[k]["lineas"] += 1
        out[k]["unidades"] += qty
        out[k]["ventas_sin_iva"] += vsi

    for v in ventas:
        pid, qty, price = v.get("product_id"), _f(v.get("qty")), _f(v.get("unit_price_with_iva"))
        if not v.get("date") or not pid or qty is None or price is None:
            hit("fila_incompleta", pid or "?")
            continue
        qty_i, vsi = int(qty), qty * price / IVA
        if pid not in costo:
            hit("sin_costo", pid, qty_i, vsi)
        elif costo[pid] is not None and price / IVA < costo[pid]:
            hit("precio_bajo_costo", pid, qty_i, vsi)
        if qty < 0 or price < 0:
            hit("ventas_negativas", pid, qty_i, vsi)
    for pid in invalidos:
        out["costo_invalido"]["productos"].add(pid)
    return {k: {**v, "productos": sorted(v["productos"])} for k, v in out.items()}


def resumen(res: dict) -> dict:
    """Mismo formato que 01_calidad_datos.sql: {codigo: (productos, lineas_o_unidades, ventas_sin_iva)}.
    En SQL, sin_costo cuenta unidades y los otros dos cuentan lineas."""
    return {"sin_costo": (len(res["sin_costo"]["productos"]), res["sin_costo"]["unidades"],
                          res["sin_costo"]["ventas_sin_iva"]),
            "precio_bajo_costo": (len(res["precio_bajo_costo"]["productos"]), res["precio_bajo_costo"]["lineas"], None),
            "ventas_negativas": (len(res["ventas_negativas"]["productos"]), res["ventas_negativas"]["lineas"], None)}


def texto_no_se(res: dict) -> str | None:
    s = res["sin_costo"]
    if not s["productos"]:
        return None
    return (f"No s\u00e9: {len(s['productos'])} productos no tienen costo ({', '.join(s['productos'])}); "
            f"vendieron {crc(s['ventas_sin_iva'])} sin IVA y quedan fuera de este c\u00e1lculo.")


def bloquea(res: dict) -> bool:
    return any(res[k]["productos"] for k in BLOQUEANTES)


def comparar_con_sql(res: dict, dq_rows: list[tuple]) -> list[str]:
    """Diferencias entre las reglas en codigo y el resultado SQL (vacio = coinciden)."""
    diffs, py = [], resumen(res)
    for chequeo, productos, cantidad, ventas in dq_rows:
        p, c, v = py[chequeo]
        if int(productos or 0) != p or int(cantidad or 0) != c or (v is not None and abs((ventas or 0) - v) > 0.01):
            diffs.append(f"{chequeo}: sql=({productos}, {cantidad}, {ventas}) codigo=({p}, {c}, {v})")
    return diffs
