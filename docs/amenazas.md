# MIDAZ threat model

> SAMPLE DATA. Scope: the code and data in this repo today. Draft to review with Josué.

## What we protect

| Asset | Why it matters |
|---|---|
| Trust in the numbers | MIDAZ's whole promise is that every figure is backed by evidence |
| Zetaris credentials | Grant query access to the federated sources |
| Business data (in a real deployment) | Sales, costs and expenses are sensitive for a small shop |

## Threats and current mitigations

| # | Threat | Example | Mitigation today | Gap |
|---|---|---|---|---|
| T1 | Invented number | Agent states a profit that no query produced | Every numeric sentence needs a receipt; `tests/test_receipts.py` fails otherwise | Only the HU-02 answer is covered |
| T2 | Missing data hidden as zero | Meats with no cost counted as zero profit | View keeps `ganancia_bruta` NULL and flags `sin_costo`; answer starts with "No sé" | — |
| T3 | Dirty data skews results | Price below cost, negative lines (returns) | `sql/01_calidad_datos.sql` emits warnings into each receipt; tested with injected rows | Warnings do not yet block an answer |
| T4 | Wrong but plausible SQL | Join or VAT error changes the 80/20 | Results compared with the control sheet (`midas/control.py`) | Control sheet comes from the same generator, so it is not fully independent |
| T5 | Dialect drift on Zetaris | Same SQL returns different types or values | Assumptions documented in `sql/README.md` (including converting string values before comparing) | **Unverified on Zetaris** |
| T6 | Credential leak | API key committed to the repo | Credentials only via environment variables; `.env.example` holds names only; `.gitignore` excludes `.env`, `secrets/`, `*.key` | No automated secret scan |
| T7 | Out-of-range questions | Asking for October forecasts | Golden item G15 expects a refusal | Not yet enforced by a test |
| T8 | SQL injection via the question | User text reaching SQL | Today only fixed SQL files run; no free-form SQL from users | Will need review if an LLM writes SQL |

## Out of scope (today)

- Real customer data: the repo ships sample data only.
- Hosting, authentication and multi-user access.

## Related

- Architecture: `docs/arquitectura.md`
- Known failures (draft): `docs/11-known-failures-DRAFT.md`
