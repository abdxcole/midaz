> **Actualizacion ARGOS 2026-10-26:** HU-00 y HU-04 verificados en vivo en la PC de Abdiel: SELECT 1 por REST OK, 3 tablas federadas (opcion A) responden y `MIDAZ_ENGINE=zetaris python run.py check` da 12/12. El mapa de esquemas queda por defecto en el motor zetaris. HU-01 (Nightshift/Nemotron) sigue sin verificar.

# 11 · Backend de Josué (rama `josue/backend`, 2026-10-22)

Estado del backend que hizo Jayden A.R.I.A (bot de Josué) en el box Linux de Josué. Todo con **SAMPLE DATA**. Ninguna llave en el repo: solo nombres de variables (ver [`.env.example`](../.env.example)).

| Tarea | Estado | Dónde |
|---|---|---|
| HU-00 Zetaris `SELECT` por REST | **Bloqueado** fuera de la PC de Abdiel (falta token y org ID) | `midas/zetaris_client.py`, este doc §1 |
| HU-01 Nemotron vía Nightshift, lane fijo | **Parcial**: cliente + guardia de números + tests listos; construido y probado con mocks; **sin verificar** contra Nemotron ni Nightshift | `midas/nightshift.py`, `midas/numguard.py` |
| HU-04 motor `zetaris` | **Parcial**: motor + tests con Zetaris simulado (12/12); falta correrlo contra Zetaris real | `midas/core.py`, `sql/zetaris/01_federar_fuentes.sql` |
| Reglas de calidad en código | **Hecho** (casos finales de ARGOS #4 pendientes) | `midas/calidad.py` |
| HU-15 H-MEM | **Hecho** (port Python de la referencia + vectores oficiales) | `midas/memory.py`, `tests/test_hmem.py` |

## 1. HU-00: Zetaris

- **En el box Linux de Josué no se puede levantar Zetaris:** no hay Docker y, sobre todo, la plataforma no es pública: hace falta `zetaris-platform.zip` (Zetaris Cloud → *Run locally*), las credenciales del registro `zetarishackathon.azurecr.io` y una licencia/entitlement (guía oficial `docs/install/updated_zetaris_installation_guide.md`). Esas credenciales son de la cuenta de Abdiel. No se intentó.
- **Token de API** (oficial, `docs/connections/client-setup.md`): entrar a la UI (`http://localhost:3000`) → *Management → API Tokens* → botón **+** → copiar la llave (se ve una sola vez) a `ZETARIS_API_KEY` en el `.env` local. `401` = llave mala, crear otra. La guía pide no pedirle a un agente que la cree ni pegarla en un prompt.
- **ID de organización:** *Management → Organisation* → copiar el campo **ID** numérico (no el nombre) a `ZETARIS_ORG_ID`. `400 Not Allowed` = ID incorrecto.
- **Probar** (en la PC de Abdiel, misma consola donde se cargaron las variables): `python -m midas.zetaris_client "SELECT 1 AS one"`. Compartir con el equipo **solo la forma** de la respuesta (las claves de `data`), para fijar `parse_zetaris_data` (hoy acepta varias formas **(sin verificar)** cuál es la real).

## 2. HU-01: Nightshift + Nemotron

- Contrato (Meterless Runtime 0.90.0, `docs/agent-ready/add-meterless-provider.md` de `Meterless/Meterless`): base `http://127.0.0.1:8088/v1`, `Authorization: Bearer <token>` (el runtime lo escribe en `<stateDir>/proxy-token`), headers `meterless-app` y `meterless-scope: user`. Los ids de `GET /v1/models` son **modos de ruteo** (`meterless/auto`, `meterless/<clase>.<disposición>`), no nombres de modelo. **(sin verificar)** cómo se expone un lane Nemotron fijo: hay que copiar el id exacto de `GET /v1/models` con Nightshift corriendo y ponerlo en `MIDAZ_NEMOTRON_LANE`.
- `midas/nightshift.py`: rechaza cualquier lane con `auto`; Nemotron redacta desde `answer.json`; `midas/numguard.py` tacha toda frase con un número que no esté en un recibo (formatos `244.887`, `67,8`, `67.8`); si la respuesta tenía "No sé", el "No sé" va primero (decidido en código). Cada recibo recibe `redaccion = {provider, lane, model, frases_quitadas}` (campo opcional nuevo en `receipt.schema.json`).
- Uso: `python run.py redact` (con `NIGHTSHIFT_URL`, `NIGHTSHIFT_TOKEN` o `METERLESS_RUNTIME_TOKEN`, `MIDAZ_NEMOTRON_LANE`).
- **Estado de las pruebas:** el cliente, el prompt y la guardia están construidos y probados con mocks (tests del repo). **Sin verificar** contra Nemotron y contra Nightshift. Para el premio NVIDIA el request tiene que pasar por Nightshift.

## 3. HU-04: motor `zetaris`

- `MIDAZ_ENGINE=zetaris python run.py check`. `ZetarisEngine` usa `zetaris_client.run_sql`, convierte strings (incluida notación exponencial) antes de comparar, y por defecto mete la vista `margen_por_producto` como **CTE** (`MIDAZ_ZETARIS_VIEW=cte`), así no hace falta `CREATE VIEW` en Zetaris; con `=view` usa una vista creada allá.
- Test con un Zetaris simulado que devuelve todo como string: 12/12 contra la hoja de control.
- Federación: `sql/zetaris/01_federar_fuentes.sql` **(sin verificar)**, 3 Lightning DB separadas (o Postgres para POS) y `MIDAZ_SCHEMA_MAP`.

## 4. Reglas de calidad en código

`midas/calidad.py`: `sin_costo` (bloquea → "No sé"), `precio_bajo_costo`, `ventas_negativas` (espejo del SQL) y dos extra sin SQL: `costo_invalido`, `fila_incompleta`. `python run.py check` compara código vs SQL (`calidad_codigo_vs_sql`).

## 5. HU-15: H-MEM

- H-MEM no es una librería: es una especificación (`engines/hmem/AGENTS.md`) con referencia en TypeScript y suite de conformidad. `midas/memory.py` es un **port Python** de la referencia (commit `1742dec`, Apache-2.0): `source` y `provenance` obligatorios, fórmula híbrida de recuperación, deltas de feedback, ledger append-only, conflictos (compuerta 0,70), sleep con guardrails, dreaming con aprobación, persistencia JSON.
- Los **vectores oficiales** de conformidad (`midas/hmem_vectors/vectors.json`) corren en Python en `tests/test_hmem.py`: 7 secciones verdes. El `runner.ts` oficial no se puede correr contra Python tal cual.
- Función real: `DecisionMemory` + `answer_followup()` (HU-14) recuerdan la decisión ("subí la Coca") y responden con `sql/40_antes_despues.sql` (recibo antes/después). Sin H-MEM, HU-14 dice "No sé".
- La memoria vive en `out/hmem/memoria.json` (ignorado por git; `MIDAZ_HMEM_PATH`).

## 6. Nightshift en el box Linux de Josué (2026-10-22 18:30 CR): no se puede

Investigado en las fuentes oficiales (`Meterless/Meterless`: `README.md`, `docs/products/nightshift/editions.md`, `hotspot.md`, `docs/architecture/stack-overview.md`, release `v1.0.6`; y `meterless.ai/engines.html`):

- Nightshift son dos paquetes **propietarios**: el *Meterless Runtime* (daemon que expone `http://127.0.0.1:8088/v1`) y la cabina de escritorio. No están en el repo Apache-2.0.
- Ediciones: **Web** (navegador, **sin hotspot**: no expone la API para apps), **Windows 10/11 x64 con GPU dedicada** (versión 1.2.1, con hotspot), **Mac M5+** (preventa US$199), **Mac M1+** (gratis, endpoint local), **DGX Spark** (a pedido). El release dice textualmente: "macOS and Linux are not supported yet".
- No hay paquete npm ni pip (`meterless` da 404 en los dos), ni binario Linux, ni imagen Docker. El box tampoco tiene GPU.
- Conclusión: **en el box no se instaló nada**. No se armó un "Nightshift falso": para el premio NVIDIA el request tiene que pasar por el Nightshift real.

### Pasos para levantarlo donde sí corre (PC Windows con GPU dedicada, de Josué o Abdiel) **(sin verificar en la práctica)**

1. Bajar el instalador de <https://www.meterless.ai/windows.html> e instalar (ojo: el instalador cierra todo `llama-server.exe` de la PC).
2. En Nightshift → **Providers**: agregar NVIDIA (build.nvidia.com) y pegar la llave NVIDIA ahí. Nunca en el repo, en mensajes ni en la herramienta de código.
3. Elegir o crear un lane que use un modelo Nemotron (p. ej. `nvidia/nemotron-3.5-lightning-30b-a3b`) **(sin verificar cómo lo nombra la UI)**.
4. Token: el runtime lo escribe en `<stateDir>/proxy-token` (o lo da la pantalla de conexión). Va en `NIGHTSHIFT_TOKEN` o `METERLESS_RUNTIME_TOKEN` del `.env` local.
5. Id del lane: `GET http://127.0.0.1:8088/v1/models` con el token; copiar el id que apunte al lane Nemotron (nunca `meterless/auto` ni otro con `auto`) a `MIDAZ_NEMOTRON_LANE`. Los ids son modos `meterless/...`; si ninguno fija Nemotron, preguntar en el Discord de Meterless.
6. Prueba de punta a punta en esa PC: `python run.py redact`. Esperado: texto redactado, ninguna frase `[TACHADA]` y `redaccion.model` anotado en cada recibo de `out/answer.json`.
7. Otra opción: dejar el runtime en esa PC y usarlo desde otra máquina en modo hotspot con el *connect link* (`http://<host>:<puerto>/connect#k=<llave>`): la base es `<origen>/v1` y la llave es el token (no se loguea).
