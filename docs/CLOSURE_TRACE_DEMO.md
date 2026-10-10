# Closure-Trace submission demo

Closure-Trace reviews alert closures and investigation gaps. This checkout does
not contain the separate scam, impersonation or campaign investigation product.
SAT-SA is the inherited analytical foundation; TRUST-SAT is its integrity layer.

## Preparation

Follow the fresh-clone install in the root README. Use Python 3.10+ and Node 24+.
Install Python dependencies from `requirements.txt` and the repository with
`python -m pip install -e . --no-deps`. The development requirements include the
bundled PostgreSQL driver so configuration tests work without system libpq.
The demo database is SQLite; a PostgreSQL server is not required.

Start the backend before recording:

```bash
python scripts/local_stack.py --seed-demo
```

In another terminal:

```bash
cd web
npm ci
npm run build
```

Linux/macOS:

```bash
SATSA_API_BASE_URL=http://127.0.0.1:8000 npm run start -- --hostname 127.0.0.1
```

Windows PowerShell:

```powershell
$env:SATSA_API_BASE_URL = "http://127.0.0.1:8000"
npm run start -- --hostname 127.0.0.1
```

Open `http://127.0.0.1:3000`. Local sign-in credentials are generated in
`.satsa-local/credentials.json`. Use the analyst for intake and the supervisor
for the final decision. Keep credentials, database, ledger and keys out of the
recording and out of Git. A startup failure now exits unsuccessfully and stops
the child API/worker processes rather than leaving an apparently ready stack.

Preload the synthetic examples and leave the primary run awaiting review. The
five entities are CSE-EXEC, CSE-HEALTHY, CSE-NEG, CSE-ANOM and CSE-PEER. Inputs
are the actual committed CSV files in `docs/demo/submissions/`. Repeating
`--seed-demo` reuses the same idempotency keys; it does not reset a recorded
decision. To prepare a fresh recording, use a separate demo directory:

```bash
python scripts/local_stack.py --data-dir .satsa-local-recording --seed-demo
```

Do not delete a populated user database to reset the demo. The isolated
rehearsal below resets automatically by creating new temporary state.

## Three-minute story

These are recording targets, not measured user completion times.

| Time | Screen/action | Explain |
|---|---|---|
| 0:00–0:20 | Workbench | "A closed alert is not necessarily an investigated alert. Closure-Trace checks what happened before closure." |
| 0:20–0:45 | CSE-EXEC run | Show premature closure, critical alerts without escalation, recurring cases without remediation, and the evidence behind them. All input is synthetic. |
| 0:45–1:10 | Finding detail | Open a signal. Show the cited source row, rationale, confidence and limitation. Risk and evidence confidence are different concepts. |
| 1:10–1:30 | Risk and recommendations | Explain which dimensions drive the score and the bounded action suggested to the reviewer. A score is not a fraud verdict. |
| 1:30–1:50 | Reviewer briefing | Show provider/model provenance if a real provider ran; otherwise say "deterministic briefing, no language model configured." |
| 1:50–2:20 | Supervisor decision | Review the evidence, select Confirm, enter a reason and record the decision. The worker finalizes after human review. |
| 2:20–2:40 | TRUST-SAT panel | Click Verify now. Show VERIFIED, the digest and ML-DSA-65 receipt. The signed record binds the review; it does not prove truth. |
| 2:40–3:20 | Isolated rehearsal output | Demonstrate a real risk-field change, INCONSISTENT, and VERIFIED after restoration. Explain that the signature still verifies but the changed state does not. |

Use the existing healthy example to demonstrate contrast if time permits. Do
not claim field accuracy or zero false positives from these synthetic cases.

## Real tamper rehearsal

From the repository root, after the web build:

```bash
python scripts/rehearse_closure_trace.py --web
```

The command starts a real API and worker in a newly created temporary directory,
uploads all five synthetic submissions through the actual API, waits for
analysis, records a synthetic supervisor decision on CSE-EXEC and verifies it.
It independently verifies the receipt signature using the public key, changes
the stored risk total without modifying the receipt, checks the API returns
`inconsistent`, restores the exact original risk JSON and verifies again. The
existing four HTTP UI smoke checks then run against a real production web server.

The rehearsal explicitly disables model providers for this disposable process.
It never changes your configured application or existing database. It does not
print generated credentials, key material or provider secrets. It requires the
local Python/Node dependencies but no cloud account or model API key. Alternate
ports are available with `--port` and `--web-port`.

Expected summary:

```json
{
  "result": "CLOSURE-TRACE REHEARSAL PASSED",
  "entities": 5,
  "runs": 5,
  "primary": "CSE-EXEC",
  "briefing": "deterministic",
  "human_decision": "confirm",
  "verification": "verified",
  "algorithm": "ML-DSA-65",
  "tamper": {
    "signature_valid": true,
    "changed_state": "inconsistent",
    "restored_state": "verified"
  },
  "web_smoke": "passed"
}
```

IDs and run times vary. In the inspected environment the primary run produced
nine signal findings; this is measured output, not a required universal count.
The 8.15-second first rehearsal covered startup, seeding, analysis, decision,
signing, tamper/restoration and smoke tests with dependencies already installed
and the frontend already built. It excludes installation and build time.

For a broader controlled integrity check:

```bash
python scripts/run_trust_integrity_experiment.py --out .satsa-local/trust-check
```

The inspected run detected all 13 material mutations and kept its one unsigned
operational-field control valid. This is engineering evidence on synthetic
state, not a real-world detection accuracy benchmark.

## AI claims

The model-assisted capability is a reviewer briefing from structured results.
It cannot set risk, create findings or decide. Source text is excluded from the
briefing input. Strict output validation rejects extra decision/risk fields.
See `docs/LLM.md` for real provider configuration and fallback behavior.

The advisory learned model is a separate mechanism. With no deployed model,
its score explicitly abstains. Do not describe an abstention as an AI prediction,
or the deterministic briefing as a live language model response.

## Checks and recovery

```bash
python -m pytest tests -q
python -m compileall -q satsa qsmlops scripts
```

In `web/`:

```bash
npm run check
# Against a running frontend:
npm run test:ui
# Requires an installed browser; starts its own isolated backend:
npx playwright install chromium
npm run test:e2e
```

Run browser E2E on the recording machine before submission. Browser binary
downloads were blocked in the inspection environment; HTTP smoke checks do
not replace it. SQLite paths passed; optional PostgreSQL/HSM/S3 tests require
their own services and remain explicitly skipped when unavailable.

If analysis fails, inspect `.satsa-local/api.log` and `worker.log`. If a run is
still awaiting review, use a supervisor to decide; an analyst cannot. If
verification is unavailable or inconsistent, show that state honestly and do
not call the record verified. Keep the signed original state unchanged for the
main recording; use the disposable rehearsal for the destructive demonstration.

## UI handoff

Preserve assets, animations, API contracts, permission enforcement and trust
semantics. The next UI pass should focus on:

1. Replace active SAT-SA/SIH product copy with Closure-Trace/ForgeHacks while
   retaining source attribution and TRUST-SAT as the integrity component.
2. Change active repository CTAs to `PrathamKapoor/Closure-Trace`; they currently
   point at `SAT-SA-with-PQC` in `web/src/components/landing/root/content/site.ts`.
3. Make CSE-EXEC → source evidence → briefing → supervisor decision → verification
   the primary visible path. Keep MLOps/admin screens out of the short demo.
4. Label deterministic briefing, model abstention, human decision and live
   verification separately. Never equate a stored receipt with current validity.
5. Replace the landing page's historical demo counters and unconditional
   "zero network calls anywhere" claim with current, accurately scoped copy.
6. Record the actual application and publish the required video separately.

No remote repository writes, pushes or pull requests are performed by the
rehearsal or these setup commands. MIT licensing and attribution remain intact.
