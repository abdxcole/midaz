# HU-00 — Zetaris en Docker y un SELECT por REST

> **Verificado en vivo 2026-10-26:** `SELECT 1` por REST OK; las 3 tablas federadas responden (`midaz_pos.ventas_pos` 46.298 filas, `midaz_inventario.costos_inventario` 197, `midaz_finanzas.gastos_operativos` 24); `MIDAZ_ENGINE=zetaris python run.py check` da 12/12 contra la hoja de control.

> Fuente: repo oficial [zetaris/getting-started](https://github.com/zetaris/getting-started) (`docs/install/updated_zetaris_installation_guide.md`, `docs/connections/client-setup.md`, `scripts/zetaris_sql.py`), leído el 2026-10-21. Nada de esto se probó todavía en la PC de Abdiel (no hay Docker): todo queda **(sin verificar)** hasta el primer `SELECT 1`.

## Pasos de Abdiel (una sola vez, como admin)

1. **WSL2 + Ubuntu** (PowerShell como administrador): `wsl --install -d Ubuntu` → reiniciar si lo pide → abrir Ubuntu y crear usuario.
2. **Docker Desktop**: instalar desde <https://docs.docker.com/desktop/setup/install/windows-install/> (como admin; backend WSL2). En *Settings → Resources → WSL integration* activar Ubuntu. Darle a Docker **≥ 8 GB de RAM y 4 CPU** (la preflight falla con < 6 GB). Necesita ≥ 15 GB libres.
3. Comprobar en PowerShell normal: `docker version` y `docker compose version` (Engine ≥ 25 recomendado).
4. **Bundle**: en Zetaris Cloud → *Run locally* (<https://cloud.enterprise.zetaris.com/dashboard/download>) bajar `zetaris-platform.zip` y descomprimirlo, p. ej. en `C:\zetaris\zetaris-platform` (**fuera** de este repo).
5. **Registro**: `docker login zetarishackathon.azurecr.io` con las credenciales que da Zetaris (Abdiel las escribe en el prompt; no van a ningún archivo del repo).
6. **.env del bundle** (vive en la carpeta del bundle, nunca en este repo): fijar `ZETARIS_ADMIN_EMAIL`, `ZETARIS_ADMIN_PASSWORD` (≥ 8, mayúscula, minúscula, dígito y uno de `$ @ ! % * ? &`), `ZETARIS_ADMIN_ORG` **antes** del primer arranque. Valores locales sugeridos: `ZSPARK_DRIVER_MEM=2g`, `ZSPARK_DRIVER_CORES=2`, `ZSPARK_MASTER_URL=local[2]`, `ZETARIS_API_MAX_HEAP=1g`, `UI_PORT=3000`, `ALLOWED_ORIGINS=http://localhost:3000`, `GUI_URL=http://localhost:3000`, `ZETARIS_SEED_TPCH=true`, `COMPOSE_PROFILES` vacío.
7. Opcional (desde Ubuntu/WSL, en la carpeta del bundle): `./preflight.sh`.

## Levantar y probar

```powershell
cd <carpeta-del-repo>   # clon de margen-hackathon-2026
.\scripts\zetaris-up.ps1 -PlatformDir C:\zetaris\zetaris-platform
```

Hace `docker compose config --quiet`, `pull` (30–45 min la primera vez), `up -d`, `ps --all` y espera a que conteste `http://localhost:8888`. Esperado: `postgres`, `driver`, `api`, `ui`, `ai-datasteward` corriendo; `init` y `bootstrap` en `Exited (0)`. Verificación oficial (desde WSL, carpeta del bundle): `./verify.sh` (9 checks).

Luego:

1. Abrir <http://localhost:3000>, entrar con el admin del paso 6 y correr `SELECT 1 AS one` en el SQL Editor.
2. *Management → API Tokens → +*: crear la llave (se ve una sola vez). *Management → Organisation*: copiar el **ID** numérico.
3. En **la misma consola** (sin escribirlas en archivos):
   ```powershell
   $env:ZETARIS_API_KEY = [Net.NetworkCredential]::new('', (Read-Host "API key" -AsSecureString)).Password
   $env:ZETARIS_ORG_ID  = "<ID numérico>"
   .\scripts\zetaris-up.ps1 -SkipCompose                                   # SELECT 1 por REST
   .\scripts\zetaris-up.ps1 -SkipCompose -Sql "SHOW LIGHTNING DATABASES"
   ```
   O con Python: `python -m midas.zetaris_client "SELECT 1 AS one"`.

## Contrato REST (de `scripts/zetaris_sql.py` oficial)

```
POST http://localhost:8888/api/v1.0/sql-editor/sqls/run
Authorization: Bearer $ZETARIS_API_KEY
X-Org-ID: $ZETARIS_ORG_ID
X-Request-ID: <uuid nuevo>
Content-Type: application/json

{"queryId": "<uuid>", "sql": "SELECT 1 AS one", "source": "SqlEditor", "limit": 100}
```

- Respuesta: JSON con `data`; la forma exacta de filas/columnas dentro de `data` está **(sin verificar)**. Los valores llegan como **string** y los decimales pueden venir en notación exponencial.
- `401` = llave mala → crear otra. `400` = `X-Org-ID` no es el ID numérico o `X-Request-ID` no es UUID.
- Docs de la API en vivo: <http://localhost:8888/redoc/index.html>.
- La UI usa otra ruta (`POST /api/proxy/sql-editor/sqls/run-query` en :3000); no la usamos.

## Parar

En la carpeta del bundle: `docker compose stop` (conserva datos) / `docker compose start`.

## Pendiente (Josué, HU-04) **(sin verificar)**

- Registrar las 3 fuentes por separado (propuesta: ventas en Postgres con `CREATE DATASOURCE`, costos y gastos como CSV/Lightning DB) y ajustar prefijos con `MIDAZ_SCHEMA_MAP`.
- Si Zetaris no deja `CREATE VIEW` sobre fuentes federadas, usar la SQL de la vista como CTE o la capa semántica.
