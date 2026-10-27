"""Cliente de Meterless Nightshift (OpenAI-compatible) para que Nemotron redacte (HU-01).

Contrato (Meterless Runtime 0.90.0, docs/agent-ready/add-meterless-provider.md del repo
Meterless/Meterless, leido 2026-10-22):
  - base `<host>/v1` (por defecto http://127.0.0.1:8088/v1), `POST /v1/chat/completions`.
  - `Authorization: Bearer <token>`; headers `meterless-app` en todo request y
    `meterless-scope: user` en chat. `GET /v1/models` decide online/unauthorized/offline.
Variables (solo nombres; valores en el .env local, nunca en el repo):
  NIGHTSHIFT_URL, NIGHTSHIFT_TOKEN (o METERLESS_RUNTIME_TOKEN), MIDAZ_NEMOTRON_LANE.
Regla: lane FIJO. Cualquier id con `auto` (p. ej. `meterless/auto`) se rechaza antes de llamar.
La llave NVIDIA no aparece aca: vive solo en Nightshift > Providers.
"""
from __future__ import annotations

import json
import os
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from . import numguard
from .prompts import SYSTEM_PROMPT

DEFAULT_URL = "http://127.0.0.1:8088/v1"
APP_ID = "midaz"
TIMEOUT = 180


class NightshiftError(RuntimeError):
    pass


def normalize_url(url: str | None) -> str:
    """Acepta lo que se pegue (con o sin esquema, /v1, /v1/chat/completions, /v1/models, /healthz)."""
    u = (url or DEFAULT_URL).strip().rstrip("/")
    if not re.match(r"^https?://", u):
        u = "http://" + u
    u = re.sub(r"(/v1)?(/chat/completions|/models|/healthz)?$", "", u)
    return u + "/v1"


def check_lane(lane: str | None) -> str:
    if not lane:
        raise NightshiftError("Falta MIDAZ_NEMOTRON_LANE (id de un lane Nemotron fijo, copiado de GET /v1/models).")
    if "auto" in lane.lower():
        raise NightshiftError(f"Lane {lane!r} prohibido: nunca meterless/auto, el lane tiene que ser fijo.")
    return lane


def _token() -> str:
    tok = os.environ.get("NIGHTSHIFT_TOKEN") or os.environ.get("METERLESS_RUNTIME_TOKEN")
    if not tok:
        raise NightshiftError("Falta NIGHTSHIFT_TOKEN o METERLESS_RUNTIME_TOKEN en el entorno.")
    return tok


def _post(path: str, body: dict | None, url: str | None = None) -> dict:
    base = normalize_url(url or os.environ.get("NIGHTSHIFT_URL"))
    headers = {"Authorization": f"Bearer {_token()}", "meterless-app": APP_ID,
               "Content-Type": "application/json"}
    if body is not None:
        headers["meterless-scope"] = "user"
    req = Request(base + path, data=json.dumps(body).encode() if body is not None else None,
                  method="POST" if body is not None else "GET", headers=headers)
    try:
        with urlopen(req, timeout=TIMEOUT) as r:
            return json.loads(r.read().decode() or "{}")
    except HTTPError as e:
        kind = "unauthorized" if e.code in (401, 403) else f"HTTP {e.code}"
        raise NightshiftError(f"{kind}: {e.read().decode(errors='replace')[:300]}") from e
    except (URLError, OSError) as e:
        raise NightshiftError(f"offline: no llego a {base} ({getattr(e, 'reason', e)})") from e


def models(url: str | None = None) -> list[str]:
    return [m["id"] for m in _post("/models", None, url).get("data", [])]


def chat(messages: list[dict], lane: str | None = None, transport=None, **kw) -> tuple[str, str]:
    """Devuelve (texto, modelo que respondio). `transport(path, body)` permite tests sin red."""
    lane = check_lane(lane or os.environ.get("MIDAZ_NEMOTRON_LANE"))
    body = {"model": lane, "messages": messages, "temperature": 0, **kw}
    out = (transport or _post)("/chat/completions", body)
    text = out["choices"][0]["message"]["content"] or ""
    return text, out.get("model") or lane


def build_messages(answer: dict) -> list[dict]:
    blocks = "\n".join(f"[{c['receipt_id']}] {c['text']}" for c in answer["claims"])
    user = ("Owner question: " + answer["question"] + "\n"
            "Facts (one per receipt; these are the ONLY numbers you may use, copy them exactly):\n"
            + blocks + "\n\nRewrite these facts for the owner in Spanish (Costa Rica), 2-4 short warm "
            "sentences. Keep the first fact first. Cite [receipt_id] after every sentence with a number. "
            "Do not compute, round or add any number.")
    return [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user}]


def redact(answer: dict, results: dict | None = None, lane: str | None = None, transport=None,
           provider: str = "nightshift") -> dict:
    """Nemotron redacta desde answer.json; la guardia quita frases con numeros sin recibo.

    Anota en cada recibo `redaccion` = {provider, lane, model, frases_quitadas}.
    """
    text, model = chat(build_messages(answer), lane=lane, transport=transport)
    allowed = numguard.allowed_numbers(answer, results)
    clean, report = numguard.strike(text, allowed)
    struck = [r for r in report if not r["keep"]]
    if not clean.strip():  # todo tachado: queda el texto deterministico
        clean = answer["answer"]
    nose = next((c["text"] for c in answer["claims"] if c["text"].startswith("No s\u00e9")), None)
    if nose and not clean.startswith("No s\u00e9"):  # HU-12: el "No se" va primero, decidido en codigo
        clean = nose + " " + clean
    meta = {"provider": provider, "lane": lane or os.environ.get("MIDAZ_NEMOTRON_LANE"),
            "model": model, "frases_quitadas": len(struck)}
    for r in answer["receipts"]:
        r["redaccion"] = meta
    return {"text": clean, "raw": text, "model": model, "struck": struck, "meta": meta}
