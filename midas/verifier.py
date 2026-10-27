"""Verificador (HU-13): da a cada recibo un veredicto real en vez de "pendiente".

Por cada recibo:
  1. Re-ejecuta su SQL exacta contra el mismo motor (local o zetaris).
  2. Compara las filas nuevas con las filas que respaldaron la respuesta.
  3. Revisa que cada numero de la frase salga de esas filas (numguard), salvo las
     constantes de la definicion (20 % / 80 % / 90 dias), que no son datos.
Veredicto: "confirmado" si todo cuadra; "rechazado" con la razon si no. Una frase con
recibo rechazado no se muestra: se reemplaza por un "No se" (sin evidencia, MIDAZ no afirma).
El verificador Nemotron (una llamada por respuesta, via Nightshift) es aparte y sigue pendiente.
"""
from __future__ import annotations

import datetime as dt
import math

from . import numguard

BY = "midaz-verificador (re-ejecucion SQL + numeros en codigo)"
NO_SE = "No s\u00e9: no pude confirmar este dato con los datos."
CONSTANTES = {20.0, 80.0, 90.0}  # 20 % / 80 % de la regla y ventana de 90 dias (definiciones, no datos)


def _same(a, b) -> bool:
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
        return math.isclose(float(a), float(b), rel_tol=1e-9, abs_tol=0.005)
    return str(a) == str(b)


def same_rows(old: list, new: list) -> str | None:
    """None si coinciden; si no, la razon."""
    if len(old) != len(new):
        return f"filas distintas al re-ejecutar: {len(old)} vs {len(new)}"
    for i, (ro, rn) in enumerate(zip(old, new)):
        if len(ro) != len(rn) or not all(_same(x, y) for x, y in zip(ro, rn)):
            return f"la fila {i + 1} cambio al re-ejecutar"
    return None


def row_numbers(rows: list) -> set[float]:
    out: set[float] = set()
    for row in rows:
        for v in row:
            if isinstance(v, bool) or v is None:
                continue
            if isinstance(v, (int, float)):
                f = float(v)
                out |= {f, round(f), round(f, 1), round(f, 2)}
            else:
                for t in numguard.numbers_in(str(v)):
                    out |= numguard.readings(t)
    return out


def derived_numbers(rows: list) -> set[float]:
    """Lo que la frase puede contar de las filas: cuantas son y la suma de cada columna numerica."""
    out = {float(len(rows))}
    for col in zip(*rows):
        nums = [float(v) for v in col if isinstance(v, (int, float)) and not isinstance(v, bool)]
        if nums and len(nums) == len(col):
            s = sum(nums)
            out |= {s, round(s), round(s, 1), round(s, 2)}
    return out


def verify_receipt(engine, receipt: dict, old_rows: list | None) -> dict:
    now = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    try:
        _cols, rows, _ms = engine.run(receipt["sql"])
    except Exception as e:  # sin re-ejecucion no hay evidencia
        return {"verdict": "rechazado", "by": BY, "checked_at": now,
                "notes": f"no se pudo re-ejecutar la SQL: {str(e)[:160]}"}
    rows = [tuple(r) for r in rows]
    if not rows:
        return {"verdict": "rechazado", "by": BY, "checked_at": now, "notes": "la SQL no devolvio filas: sin evidencia"}
    if old_rows is not None:
        diff = same_rows([tuple(r) for r in old_rows], rows)
        if diff:
            return {"verdict": "rechazado", "by": BY, "checked_at": now, "notes": diff}
    allowed = row_numbers(rows) | derived_numbers(rows) | CONSTANTES
    bad = numguard.unsupported(receipt["claim"], allowed)
    if bad:
        return {"verdict": "rechazado", "by": BY, "checked_at": now,
                "notes": f"numeros de la frase que no salen de las filas: {', '.join(bad)}"}
    return {"verdict": "confirmado", "by": BY, "checked_at": now,
            "notes": f"SQL re-ejecutada en {engine.name}: {len(rows)} filas iguales; todos los numeros de la frase salen de las filas"}


def no_se(receipt: dict) -> str:
    """Texto publico generico: la razon detallada (p. ej. el error del motor) queda solo en el recibo."""
    return NO_SE


def verify_answer(engine, ans: dict) -> dict:
    """Pone el veredicto en cada recibo y reemplaza por "No se" las frases sin evidencia."""
    by_file = {q["file"]: q["rows"] for q in ans.get("results", {}).values()}
    for r in ans["receipts"]:
        r["verifier"] = verify_receipt(engine, r, by_file.get(r["sql_file"]))
    rid = {r["id"]: r for r in ans["receipts"]}
    for c in ans["claims"]:
        r = rid.get(c["receipt_id"])
        if r is None or r["verifier"]["verdict"] != "confirmado":
            c["text"] = no_se(r) if r else "No s\u00e9: esta frase no tiene recibo."
            c["verified"] = False
        else:
            c["verified"] = True
    ans["answer"] = " ".join(c["text"] for c in ans["claims"])
    ans["verification"] = {"confirmados": sum(c["verified"] for c in ans["claims"]), "total": len(ans["claims"])}
    return ans