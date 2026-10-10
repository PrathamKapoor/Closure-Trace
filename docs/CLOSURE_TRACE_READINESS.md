# Closure-Trace readiness check — 10 October 2026

## Verification scope

This snapshot covers the Closure-Trace supervisory alert-closure product: fresh
installation, dependency manifests, local startup and seed flow, orchestration,
reviewer briefing, human decisions, integrity verification, application integration
and regression tests. It describes the tested configuration, not a production
certification. Original implementation history and MIT attribution are preserved.

## Corrections

| Problem | Change |
|---|---|
| A failed/cancelled analysis could count as finished demo setup | Seed waiting now refuses unsuccessful/unknown terminal states and empty runs; resuming remains pending. |
| Invalid submissions could be silently skipped | Seeding now exits unsuccessfully on invalid validation or an empty dataset. |
| API and worker could survive a failed bootstrap/seed | Startup reaps both processes on failure; shutdown has a bounded terminate/kill fallback. |
| An unexpectedly exited child could produce a successful launcher exit | The launcher now returns failure unless stopped by the user. |
| Fresh test installation failed without system libpq | Both development manifests now include `psycopg[binary]>=3.2,<4`; runtime requirements stay unchanged. |
| Alternate local demo folders could expose generated material to Git | `.satsa-local*/` is ignored, including the documented recording directory. |
| No single Closure-Trace submission rehearsal | Added a disposable, real API/worker/signing/tamper/restoration rehearsal and the demo guide. |
| README opening obscured the submission problem | Opening now describes alert-closure gaps, human review and the integrity boundary; inherited attribution remains. |

No database migration, crypto algorithm, global confidence invariant, production
rate limit, existing test assertion, asset or animation was changed.

## Measured verification

Environment: Python 3.12.14, Node 24.19.0, npm 11.9.0; fresh virtual environment
and `npm ci`; local SQLite database; no model provider; no cloud services.

| Check | Actual result |
|---|---|
| Full Python suite after the dependency correction | **1,518 passed, 262 skipped, 0 failed**, 412.48 seconds |
| Focused API contract, authorization, tenancy, adversarial trust, finalization, model fallback/graph and offline checks | **101 passed, 76 skipped** |
| New demo failure/recovery regression tests | **13 passed** |
| Post-commit demo, tracked-secret and manifest checks | **20 passed** |
| Frontend `npm run check` | Lint, type checking and production build all passed |
| Running-server HTTP UI smoke checks | **4 passed** |
| Browser E2E, existing real-backend workbench suite | **11 passed**, no skips/failures/flaky results; 39.78 seconds |
| `compileall` | Exit 0 |
| Bandit, high-severity gate over `satsa`, `qsmlops`, `scripts` | Exit 0, no reported HIGH findings |
| `pip check`, `git diff --check` | Passed |

The original full run exposed seven AWS configuration-test failures caused by
missing libpq. Installing the bundled driver and updating the dev manifests
resolved all seven; the subsequent full suite passed. Tests were not disabled.
The skipped tests depend on unavailable optional services/providers, notably
PostgreSQL and HSMs. They are not claimed as verified here.

The standard Playwright download returned invalid browser archives. Browser
verification then used an environment-only Chromium 153 executable and a
temporary configuration outside the repository. It selected a loopback host
and set `SATSA_MUTATION_RATE_LIMIT=2000`, `SATSA_READ_RATE_LIMIT=10000` only for
the throwaway test backend. Production defaults and committed tests remain
unchanged. The separate rate-limit regression checks also passed. The verified
suite covers actual browser intake, validation, analysis, risk/findings,
supervisor decision, signing/verification, audit permissions and logout.

## Demonstrated trust property

`python scripts/rehearse_closure_trace.py --web` ran successfully twice, taking
8.15 and 6.93 seconds with dependencies installed and the frontend already built.
Five synthetic entities and runs were created; CSE-EXEC produced nine signal
findings. Briefing provenance was `deterministic`, not a pretend model response.
A supervisor confirmation led to a real ML-DSA-65 receipt and API verification.

The rehearsal independently verified the signature with the receipt public
key, changed the signed state's stored risk total, and received `INCONSISTENT`.
It restored the exact original JSON and received `VERIFIED`. Verification uses
the application's actual status vocabulary.

The existing controlled integrity experiment independently detected **13/13
material mutations** and preserved **1/1 unsigned operational-field controls**.
That is evidence about these controlled mutations, not a detection accuracy
metric or a universal tamper-resistance claim.

## Remaining submission work

Backend/demo readiness is verified for the tested local configuration. Final
submission readiness still requires the UI and recording work:

1. Active landing and application copy still uses SAT-SA/TRUST-SAT and SIH.
   Brand the product Closure-Trace and identify TRUST-SAT as its integrity layer.
2. Repository links now target Closure-Trace. Verify all presentation copy and
   links again when polishing the interface.
3. Historical landing counters (seven entities, twelve runs, eighty-five
   signals) are not the current five-entity golden scenario. Scope or remove
   those counters; do not present them as live statistics.
4. The optional reviewer LLM was not exercised with a real paid provider here.
   Configure and rehearse a real provider if the recording promises live model
   assistance. Otherwise label deterministic briefing and model abstention.
5. Record the 2–4 minute video and complete the actual submission form. Neither
   a video nor a hosted Closure-Trace deployment was created in this check.
6. Re-run the browser path after UI changes. Preserve assets and animations,
   human decision requirements, authorization and live verification semantics.

The signature binds the recorded review; it proves neither real-world evidence
truth nor analytical correctness. The local software PQC implementation and
database/ledger/key trust boundary retain the limitations in `docs/TRUST_MODEL.md`.
MIT licensing and source attribution are preserved.

## Reproduce locally

Follow the installation commands in the root README, install dependencies in a
virtual environment, and build the frontend with `npm run check` from `web/`.
Then run:

```bash
python scripts/rehearse_closure_trace.py --web
```

See [the demo guide](CLOSURE_TRACE_DEMO.md) for the live presentation workflow,
reset commands and recovery steps. Use the current `main` branch; do not apply an
older patch over already-published changes.
