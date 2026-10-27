# MIDAZ — "Turn your data into gold."

MIDAZ is a text money assistant (voice planned) for a small Costa Rican shop (pulpería / mini-super). The owner asks plain questions in Spanish ("¿Qué productos me dan la plata?", "¿Me alcanza este mes?") and MIDAZ answers **only with numbers it can back with a receipt**: every figure points to the SQL file that produced it, the row count and the run time. When the data can't answer, it says "No sé" instead of guessing.

Built for the **Open Agent Hackathon 2026**, track **02 · The Agent That Can Explain Why** (code freeze Mon Oct 26, 12:00 PM CR). **All data is SAMPLE DATA**; nothing here describes a real business.

## Probar MIDAZ sin Zetaris

Los jueces pueden correr MIDAZ en modo muestra, sin Zetaris, sin Docker y sin llaves. Zetaris está en la máquina del equipo; el video del pitch es la prueba en vivo contra esas fuentes.

Hace falta Python 3.10+. Los datos son de ejemplo.

```bash
python run.py       # demo en la consola: respuestas y recibos
python run.py ui    # pantalla local en http://127.0.0.1:8765
```

La pantalla pregunta en español, deja la respuesta en grande y, debajo, la prueba: el SQL, las filas usadas, las fuentes (POS, inventario, finanzas) y el sello del verificador (confirmado, o No sé si lo rechaza).

## How to run the demo

Requirements: Python 3.10+. The offline commands (`python run.py`, `test`, `check`) need no Docker and no keys.

```bash
python run.py          # full demo: answers + receipts (SAMPLE DATA, local SQLite stand-in)
python run.py ui       # local screen on http://127.0.0.1:8765 (see "Probar MIDAZ sin Zetaris" above)
python run.py followup # only the H-MEM follow-up (HU-14); add a question in quotes to ask another
python run.py test     # 79 unit tests (same as: python -m unittest discover -s tests); does not read .env
python run.py check    # compare SQL results against the control sheet (data/output/control_8020.*)
python run.py redact   # also sends the answer to Nemotron via Nightshift to draft the text
```

`redact` is **not** offline: it needs `NIGHTSHIFT_URL`, `NIGHTSHIFT_TOKEN` (or `METERLESS_RUNTIME_TOKEN`) and `MIDAZ_NEMOTRON_LANE` set by the operator, and exits with code 2 without calling Nightshift if any is missing. Nightshift is not installed or verified yet.

Running against Zetaris instead of the local stand-in:

```bash
MIDAZ_ENGINE=zetaris python run.py
```

This needs `ZETARIS_REST_URL`, `ZETARIS_ORG_ID` and `ZETARIS_API_KEY` set **by the operator** in their own environment or a local `.env` (see `.env.example` for names only). `python run.py` and `python run.py ui` load that `.env` when it is present: they never override variables already set in the environment and never print the values. No key is ever committed. With `MIDAZ_ENGINE=zetaris`, table prefixes default to the federated databases (`pos=midaz_pos,inventario=midaz_inventario,finanzas=midaz_finanzas`); `MIDAZ_SCHEMA_MAP` overrides them; `MIDAZ_ZETARIS_VIEW` picks CTE vs. view mode. Setup steps: `docs/08-hu00-zetaris.md`.

## What it shows (sample data)

- The 80/20 answer: on the sample data, the top 20 % of products with cost produce **67.8 %** of gross profit — reported as is, not rounded up to "80/20".
- Products that "sell a lot but leave little" (high units, low margin).
- "¿Me alcanza?" monthly shortfall — **PROVISIONAL** (golden items G10/G11; expense list not final).
- Honest "No sé": three products have no cost row by design, and MIDAZ excludes them and says so.

## How we use Zetaris, Meterless, NVIDIA and Cursor

- **Zetaris:** three federated sources, `midaz_pos.ventas_pos`, `midaz_inventario.costos_inventario` and `midaz_finanzas.gastos_operativos`. `MIDAZ_ENGINE=zetaris` runs the same SQL files against them through `midas/zetaris_client.py` (key set by the operator; see above). **Live check passed** on 2026-10-26 on the team's local Zetaris (REST `localhost:8888`): `SELECT 1` works, the three tables answer (46,298 / 197 / 24 rows) and `MIDAZ_ENGINE=zetaris python run.py check` gives **12/12** against the control sheet.
- **Meterless:**
  - **H-MEM engine** in `midas/memory.py`, running in the demo flow: `python run.py` (and `python run.py followup`) calls `run_followup()` in `run.py`, which uses `DecisionMemory` and `answer_followup()` (HU-14, "¿Cómo me fue con lo de la Coca?"). The owner's decision ("subí la Coca el 15 de agosto") is a **scripted first turn** of the demo, saved to H-MEM on each run. The follow-up recalls it and answers with the before/after receipt from `sql/40_antes_despues.sql`. A question that doesn't name the remembered product, or any failure, gets "No sé". Tested in `tests/test_hmem.py` (official conformance vectors) and end to end in `tests/test_run_followup.py`.
  - **Nightshift** is the primary AI provider (`midas/nightshift.py`, fixed Nemotron lane). **Not installed or verified yet.**
- **NVIDIA:** Nemotron drafts the answer text from the receipts (`redact()` in `midas/nightshift.py`). Then `strike()` in `midas/numguard.py` strikes any sentence with a number that has no receipt. Built and tested with mocks, not verified in Nightshift.
- **Cursor:** most of the code, SQL, tests and docs in this repo were written by AI coding agents running as **Cursor cloud agents**, launched on Abdiel's and Josué's Cursor accounts; part of the backend was built by Josué's own bot outside Cursor (see `docs/11-backend-josue.md`). Abdiel and Josué directed the work, reviewed it and approved every merge. `AGENTS.md` holds the working rules for those agents (e.g. never paste keys into the coding tool).

## Status

| Piece | Status |
|---|---|
| SQL + receipts on local SQLite stand-in | Built, covered by unit tests |
| Control-sheet check (`run.py check`) | Built |
| Zetaris engine (`MIDAZ_ENGINE=zetaris`) | **Verified live** (2026-10-26): 3 federated tables, `run.py check` 12/12 on Zetaris; dialect notes in `sql/README.md` |
| HU-14 follow-up with H-MEM (`run.py` → `run_followup()` → `answer_followup()`) | Built, runs in `python run.py` / `python run.py followup`; end-to-end test in `tests/test_run_followup.py` |
| H-MEM memory (`midas/memory.py`) | Built, tested against official conformance vectors (`tests/test_hmem.py`) |
| Nemotron via Nightshift (`midas/nightshift.py`, `midas/numguard.py`) | **Built and tested with mocks, not verified in Nightshift** |
| Verifier step (`midas/verifier.py`, HU-13) | Built: re-runs each receipt's SQL on the same engine, compares rows and checks every number in the sentence against them; verdict `confirmado`/`rechazado` with reason; a rejected sentence becomes "No sé". Tested (`tests/test_verifier.py`) and live on Zetaris. The Nemotron verifier call (via Nightshift) is still pending |
| Local screen (`python run.py ui`) | Built for the pitch: question, answer, SQL, rows, sources and the verifier seal. Sample data, no Zetaris required |

Known gaps per data source: `docs/11-known-failures-DRAFT.md`.

## Repo map

| Path | What |
|---|---|
| `run.py` | Entry point (demo, ui, followup, test, check, redact) |
| `midas/ui.py` | Local screen for the pitch (`python run.py ui`) |
| `midas/` | Python package (keeps its old folder name; the product is MIDAZ) |
| `sql/` | One SQL file per question; dialect notes in `sql/README.md` |
| `data/` | Sample-data generator (fixed seed) and output CSVs |
| `receipt/` | Receipt format |
| `tests/` | Unit tests and golden questions (`tests/golden.yaml`) |
| `scripts/` | Helper scripts (e.g. Zetaris startup) |
| `docs/` | Planning, architecture and decisions — index in [`docs/README.md`](docs/README.md) |

## Docs

Start with [`docs/README.md`](docs/README.md). Most useful for judges: [`docs/arquitectura.md`](docs/arquitectura.md) (architecture), [`docs/amenazas.md`](docs/amenazas.md) (threat model), [`docs/11-known-failures-DRAFT.md`](docs/11-known-failures-DRAFT.md) and [`docs/DECISIONES.md`](docs/DECISIONES.md). Planning docs (01–10) are in Spanish.

## Rules we hold ourselves to

- No number without a receipt; no invented figures.
- No keys in the repo, video or screenshots.
- Data always labeled "Sample data".

Contributors and agents: see `AGENTS.md`.
