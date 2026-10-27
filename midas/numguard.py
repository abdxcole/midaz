"""Guardia de numeros (HU-01 / HU-13): ningun numero del texto redactado puede faltar en los recibos.

Se extraen los numeros del texto (formato CR `244.887`, `67,8`, o ingles `67.8`, `1,234.5`),
se prueban todas las lecturas posibles y la frase pasa solo si alguna lectura coincide con un
numero que trae un recibo (en su `claim` o en sus filas). Las citas `[R-XXXX]` no cuentan.
"""
from __future__ import annotations

import re

NUM_RE = re.compile(r"\d[\d.,]*")
CITE_RE = re.compile(r"\[R-[A-Z0-9-]+\]")
SENT_RE = re.compile(r"(?<=[.!?])\s+(?=[^\s])")


def readings(tok: str) -> set[float]:
    """Todas las lecturas razonables de un token numerico ('244.887' -> {244887, 244.887})."""
    tok = tok.rstrip(".,")
    out = set()
    for thousands, decimal in ((".", ","), (",", "."), ("", ".")):
        s = tok.replace(thousands, "") if thousands else tok
        s = s.replace(decimal, ".")
        try:
            out.add(float(s))
        except ValueError:
            pass
    return out


def numbers_in(text: str) -> list[str]:
    return [t.rstrip(".,") for t in NUM_RE.findall(CITE_RE.sub(" ", text))]


def allowed_numbers(answer: dict, results: dict | None = None) -> set[float]:
    """Numeros permitidos: los de cada claim con recibo y los valores de las filas de resultados."""
    ids = {r["id"] for r in answer.get("receipts", [])}
    allowed: set[float] = set()
    for c in answer.get("claims", []):
        if c.get("receipt_id") in ids:
            for t in numbers_in(c["text"]):
                allowed |= readings(t)
    for r in answer.get("receipts", []):
        for t in numbers_in(r.get("claim", "")):
            allowed |= readings(t)
    for q in (results or {}).values():
        for row in q.get("rows", []):
            for v in row:
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    allowed |= {float(v), round(float(v)), round(float(v), 1), round(float(v), 2)}
    return allowed


def _ok(tok: str, allowed: set[float]) -> bool:
    return any(any(abs(x - a) < 1e-6 for a in allowed) for x in readings(tok))


def unsupported(text: str, allowed: set[float]) -> list[str]:
    """Numeros del texto que no aparecen en ningun recibo."""
    return [t for t in numbers_in(text) if not _ok(t, allowed)]


def split_sentences(text: str) -> list[str]:
    return [s for s in SENT_RE.split(text.strip()) if s]


def check(text: str, allowed: set[float]) -> list[dict]:
    """Una entrada por frase: {'sentence', 'bad_numbers', 'keep'}."""
    out = []
    for s in split_sentences(text):
        bad = unsupported(s, allowed)
        out.append({"sentence": s, "bad_numbers": bad, "keep": not bad})
    return out


def strike(text: str, allowed: set[float]) -> tuple[str, list[dict]]:
    """Quita las frases con numeros sin recibo. Devuelve (texto limpio, reporte)."""
    rep = check(text, allowed)
    return " ".join(r["sentence"] for r in rep if r["keep"]), rep
