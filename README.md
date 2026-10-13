# FDA FAERS Signal Disproportionality

A reproducible, exploratory pharmacovigilance calculator for **2 × 2 drug–event reporting tables**. Enter counts in the browser, analyze CSV batches offline, or use the Python CLI/API. No FAERS database is bundled or queried automatically.

## What it calculates

Given mutually exclusive reporting counts:

| | Target adverse event | Other events |
| --- | ---: | ---: |
| Target drug | a | b |
| Other drugs | c | d |

- **PRR:** \`[a / (a+b)] / [c / (c+d)]\`.
- **ROR:** \`(a × d) / (b × c)\`.
- **95% confidence intervals:** large-sample log-Wald intervals for PRR/ROR when all cells are positive.
- **Yates-corrected chi-square:** 1-degree-of-freedom association statistic using the original counts.
- **Crude information component:** \`log2(a / expected)\`, where \`expected = (a+b)(a+c) / N\`. **This is not a Bayesian BCPNN posterior IC**, nor does it supply an IC025 credibility bound.
- **Exploratory screening flag:** at least three co-reports, PRR ≥ 2, Yates χ² ≥ 4, with positive counts in all four cells. This deliberately conservative implementation excludes zero-cell tables from the flag. It is not a regulatory determination.

An optional Haldane–Anscombe continuity correction adds 0.5 to all four cells **only if any cell is zero**, for ratio and CI estimation. The chi-square, expected count and crude IC use the original counts. Undefined numerical results are returned as \`null\` in Python or shown as "Undefined" in the browser.

**Interpretation:** Disproportionate reporting is not an incidence rate, probability of an adverse reaction, clinical risk estimate, or proof of causality. Reporting practices, confounding by indication, duplicate reports, incomplete case data and background selection all affect results. Review underlying cases and signal-management evidence before any clinical or regulatory action.

## Browser application

Open [web/index.html](web/index.html) locally in a modern browser. No installation, backend, internet connection, telemetry or external dependency is needed.

1. Fill in the four reporting counts and select **Calculate signal**.
2. Review PRR, ROR, confidence intervals, chi-square, crude IC and the exploratory flag.
3. To process a batch, choose a CSV containing \`a,b,c,d\` header fields and optional \`drug,event\`. Use **Download sample CSV** for the format.
4. Export the analyzed CSV. Input data remains in browser memory and is never sent to this repository or a server by the static application.

The browser limits counts to 0–1,000,000 per cell for numeric precision and accepts a maximum 5 MB CSV with 10,000 records. Use the Python interface for larger integer counts.

The GitHub Pages deployment workflow publishes \`web/\` on updates to \`master\`, provided GitHub Pages is enabled with **GitHub Actions** as the build/deployment source. A public live-application URL is only published here after independent verification.

## Python installation and CLI

Python 3.9 or newer:

\`\`\`bash
python -m pip install -e ".[api,test]"
python -m pytest -v
\`\`\`

Compute a signal directly (both supported CLIs):

\`\`\`bash
fda-faers-signal-disproportionality signal --a 30 --b 70 --c 20 --d 880
python cli.py signal --a 30 --b 70 --c 20 --d 880
\`\`\`

Add \`--continuity-correction\` to handle zero-cell intervals. The command prints machine-readable JSON and exits with an error on invalid input. A package call is also available:

\`\`\`python
from faers_sentinel.disproportionality import calculate_signal

result = calculate_signal(30, 70, 20, 880)
print(result["prr"], result["ror"], result["evans_screening_flag"])
\`\`\`

## REST API

\`\`\`bash
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
python cli.py serve --host 127.0.0.1 --port 8000
\`\`\`

Open \`http://127.0.0.1:8000/\` for the browser interface, \`/docs\` for generated OpenAPI documentation, or call \`POST /api/signal\`:

\`\`\`bash
curl -s http://127.0.0.1:8000/api/signal \
  -H 'Content-Type: application/json' \
  -d '{"a":30,"b":70,"c":20,"d":880}'
\`\`\`

The original \`audit\`, \`batch\`, \`chat\` and \`verify-audit\` CLI commands, and the legacy \`/api/audit\` interface, are retained for backwards compatibility. **Those generic operational thresholds are not PRR/ROR/IC calculations and must not be treated as pharmacovigilance signal decisions.** The deterministic chat adapter does not perform clinical reasoning or call an external model.

## Security, privacy and deployment

- The browser tool runs entirely locally; no data leaves the page. Avoid importing identifiable patient-level records into a shared device.
- The Python server stores legacy task data and audit events in process memory. The audit trail is not durable across restarts and is not a substitute for controlled, persistent compliance logging.
- Set a strong \`AUDIT_SECRET_KEY\` for any server deployment. The command-line demo generates a random process-local key if absent, but a production environment must configure its own key.
- \`GET /api/audit/logs\` is denied unless \`AUDIT_VIEW_TOKEN\` is configured and supplied using an \`Authorization: Bearer <token>\` header. Use TLS and application-level access controls before exposing the API to a network.
- The identifier regex checks are incomplete and **do not establish HIPAA Safe Harbor de-identification**. Do not submit protected health information.
- Docker: \`docker build -t faers-signal .\`, then \`docker run --rm -p 8000:8000 -e AUDIT_SECRET_KEY="$AUDIT_SECRET_KEY" faers-signal\`. Docker Compose requires \`AUDIT_SECRET_KEY\` and will refuse an unset value.
- CI installs the package and runs Python 3.10–3.12 tests, Python compilation, JavaScript syntax validation and Node browser-logic smoke tests.

### Methods and caveats

See the [FDA data-mining overview](https://www.fda.gov/science-research/data-mining/data-mining-fda-white-paper) for disproportionality methodology and caveats, and [WHO pharmacovigilance guidance](https://www.who.int/docs/default-source/documents/publications/gmp/a-practical-handbook-on-the-pharmacovigilance-of-antimalarial-medicines.pdf) for the distinction between PRR and Bayesian BCPNN. Neither source endorses this software.

## Technology and license

Python standard-library statistics, optional Pydantic/FastAPI/Uvicorn server, plain JavaScript/HTML/CSS browser UI, pytest and GitHub Actions. Current Chromium, Firefox and Safari browsers are the intended targets; the interface does not require WebAssembly/Pyodide. MIT license; see [LICENSE](LICENSE).
