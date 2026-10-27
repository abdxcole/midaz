"""Cliente REST minimo de Zetaris (stdlib). Credenciales SOLO por variables de entorno.

Basado en zetaris/getting-started (scripts/zetaris_sql.py, RestChannel):
  POST {ZETARIS_REST_URL}/sql-editor/sqls/run
  headers: Authorization: Bearer <ZETARIS_API_KEY>, X-Org-ID, X-Request-ID (UUID)
  body: {"queryId": uuid, "sql": ..., "source": "SqlEditor", "limit": N}
  respuesta: Zetaris confirmo que `SELECT 1 AS one` da [["1"]]: filas como listas de texto sin
  encabezados; core.parse_zetaris_data toma los nombres del alias del SELECT y convierte numeros.

Uso: python -m midas.zetaris_client "SELECT 1 AS one"
"""
from __future__ import annotations

import json
import os
import sys
import time
import uuid
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DEFAULT_REST_URL = "http://localhost:8888/api/v1.0"


class ZetarisError(RuntimeError):
    pass


def run_sql(sql: str, limit: int = 1000, timeout: int = 600) -> tuple[object, float]:
    key = os.environ.get("ZETARIS_API_KEY")
    if not key:
        raise ZetarisError("Falta ZETARIS_API_KEY en el entorno (crearla en Management > API Tokens).")
    base = os.environ.get("ZETARIS_REST_URL", DEFAULT_REST_URL).rstrip("/")
    body = {"queryId": str(uuid.uuid4()), "sql": sql.strip().rstrip(";"), "source": "SqlEditor", "limit": limit}
    req = Request(base + "/sql-editor/sqls/run", data=json.dumps(body).encode(), method="POST", headers={
        "Authorization": f"Bearer {key}",
        "X-Org-ID": os.environ.get("ZETARIS_ORG_ID", "1"),
        "X-Request-ID": str(uuid.uuid4()),
        "Content-Type": "application/json",
    })
    t0 = time.perf_counter()
    try:
        with urlopen(req, timeout=timeout) as resp:
            out = json.loads(resp.read().decode() or "null")
    except HTTPError as e:  # 401 = llave mala; 400 = X-Org-ID malo o X-Request-ID no UUID
        raise ZetarisError(f"HTTP {e.code}: {e.read().decode(errors='replace')[:300]}") from e
    except (URLError, OSError) as e:
        raise ZetarisError(f"No llego a {base}: {getattr(e, 'reason', e)}") from e
    return (out.get("data") if isinstance(out, dict) else out), (time.perf_counter() - t0) * 1000


if __name__ == "__main__":
    data, ms = run_sql(sys.argv[1] if len(sys.argv) > 1 else "SELECT 1 AS one")
    print(json.dumps(data, ensure_ascii=False, indent=2)[:4000])
    print(f"({ms:.0f} ms)")
