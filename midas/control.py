"""Compara los resultados SQL contra la hoja de control HU-05 (data/output/control_8020.*)."""
from __future__ import annotations

import csv
import re

from .core import DATA_DIR


def _num(s: str) -> float:
    return float(s.replace(",", "").replace("*", ""))


def load_control() -> dict:
    with open(DATA_DIR / "control_8020.csv", newline="", encoding="utf-8") as f:
        ranking = list(csv.DictReader(f))
    md = (DATA_DIR / "control_8020.md").read_text(encoding="utf-8")
    m = re.search(r"\*\*(\d+)\*\*; ganancia bruta total 90 dias: \*\*CRC ([\d,]+)\*\*", md)
    t = re.search(r"Top 20% \((\d+) productos\) = \*\*([\d.]+)%\*\*", md)
    e = re.search(r"con \*\*(\d+) productos\*\*", md)
    meses = {mm: (_num(g), _num(o), _num(fa)) for mm, g, o, fa in
             re.findall(r"\| (\d{4}-\d{2}) \| ([\d,]+) \| ([\d,]+) \| \*\*([\d,]+)\*\* \|", md)}
    return {"ranking": ranking, "n": int(m[1]), "total": _num(m[2]), "ntop": int(t[1]),
            "pct_top": float(t[2]), "n80": int(e[1]), "meses": meses}


def compare(results: dict) -> list[tuple[str, bool, str]]:
    c = load_control()
    checks = []

    def chk(name, ok, detail):
        checks.append((name, bool(ok), detail))

    n, total, ntop, pct_top, n80, _ = results["resumen"]["rows"][0]
    chk("n_productos", n == c["n"], f"{n} vs {c['n']}")
    chk("ganancia_total", abs(total - c["total"]) < 1, f"{total:,.2f} vs {c['total']:,.0f}")
    chk("n_top20", ntop == c["ntop"], f"{ntop} vs {c['ntop']}")
    chk("pct_top20", round(pct_top, 1) == c["pct_top"], f"{pct_top:.2f} vs {c['pct_top']}")
    chk("n_para_80", n80 == c["n80"], f"{n80} vs {c['n80']}")

    rk = results["ranking"]
    idx = {col: i for i, col in enumerate(rk["columns"])}
    # rank_volumen: empates en unidades se desempatan distinto (SQL por product_id, el generador
    # por orden de primera venta). Vale cualquier rank dentro del grupo empatado.
    qtys = [r[idx["unidades"]] for r in rk["rows"]]
    bad, ties = [], 0
    for row, ref in zip(rk["rows"], c["ranking"]):
        q = row[idx["unidades"]]
        lo, hi = 1 + sum(x > q for x in qtys), sum(x >= q for x in qtys)
        ties += row[idx["rank_volumen"]] != int(ref["rank_volumen"])
        if (row[idx["product_id"]] != ref["product_id"]
                or not lo <= int(ref["rank_volumen"]) <= hi
                or row[idx["unidades"]] != int(ref["qty"])
                or abs(row[idx["ganancia_bruta"]] - float(ref["ganancia_bruta_sin_iva"])) > 0.01
                or abs(row[idx["pct_acumulado"]] - float(ref["pct_acumulado"])) > 0.01):
            bad.append(ref["rank_ganancia"])
    chk("ranking_completo", len(rk["rows"]) == len(c["ranking"]) and not bad,
        f"{len(rk['rows'])} filas, diferencias: {bad[:10] or 'ninguna'} "
        f"({ties} rank_volumen distintos solo por desempate de unidades iguales)")

    arroz = next(r for r in results["volumen"]["rows"] if r[3] == "P001")
    chk("arroz_vol1_gan8", (arroz[0], arroz[1]) == (1, 8), f"vol #{arroz[0]}, ganancia #{arroz[1]}")

    for mes, g, o, fa, _ in results["mes"]["rows"]:
        cg, co, cf = c["meses"][mes]
        chk(f"faltante_{mes}", abs(g - cg) < 1 and o == co and abs(fa - cf) < 1,
            f"ganancia {g:,.0f} gastos {o:,.0f} faltante {fa:,.0f} vs {cf:,.0f}")

    sin = [r[0] for r in results["sin_costo"]["rows"]]
    chk("sin_costo_carnes", sin == ["P007", "P008", "P009"], f"{sin}")
    return checks
