"""Rehearse Closure-Trace against a fresh, disposable local API and worker.

Uploads the real synthetic CSVs, runs analysis, records a synthetic human
decision, verifies ML-DSA-65, changes one signed risk field, and verifies
that the API rejects the changed state. Always restores the field and
removes the scratch database/keys. Never opens an existing user database.
Use --web to also run the existing HTTP UI smoke checks against a local
production build. No model credentials, cloud service or Git operation.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from local_stack import _stop_processes, start
from seed_demo_via_api import Api, seed, wait


def tamper_check(api: Api, data: Path, run_id: str, receipt: dict) -> dict:
    from qsmlops.crypto.providers import SIGNATURE_PROVIDERS
    from qsmlops.database.engine import create_engine

    provider = SIGNATURE_PROVIDERS[receipt["algorithm_id"]]
    signature_valid = provider.verify(
        base64.b64decode(receipt["public_key_b64"]),
        receipt["content_digest"].encode("utf-8"),
        base64.b64decode(receipt["signature_b64"]),
    )
    if not signature_valid:
        raise RuntimeError("receipt signature failed independent verification")
    db = create_engine(f"sqlite:///{(data / 'satsa.db').as_posix()}")
    org = api.headers["X-Organization-ID"]
    try:
        row = db.query_one(
            "SELECT profile_json FROM satsa_run_risk WHERE organization_id=? AND run_id=?",
            (org, run_id),
        )
        original = row["profile_json"]
        changed = json.loads(original)
        changed["total_score"] += 1
        try:
            db.execute(
                "UPDATE satsa_run_risk SET profile_json=? WHERE organization_id=? AND run_id=?",
                (json.dumps(changed), org, run_id),
            )
            result = api.call("POST", f"/api/v1/runs/{run_id}/verify")
            if result["status"] != "inconsistent":
                raise RuntimeError("changed investigation state was not rejected")
        finally:
            db.execute(
                "UPDATE satsa_run_risk SET profile_json=? WHERE organization_id=? AND run_id=?",
                (original, org, run_id),
            )
        restored = api.call("POST", f"/api/v1/runs/{run_id}/verify")
        if restored["status"] != "verified":
            raise RuntimeError("restored original state does not verify")
        return {"signature_valid": signature_valid, "changed_state": result["status"],
                "restored_state": restored["status"]}
    finally:
        db.close()


def web_smoke(data: Path, api_url: str, port: int) -> None:
    executable = ROOT / "web" / "node_modules" / "next" / "dist" / "bin" / "next"
    if not executable.exists() or not (ROOT / "web" / ".next" / "BUILD_ID").exists():
        raise RuntimeError("run npm ci and npm run build in web/ before --web")
    env = {**os.environ, "SATSA_API_BASE_URL": api_url,
           "SAT_SA_BASE_URL": f"http://127.0.0.1:{port}"}
    with (data / "web.log").open("w") as log:
        web = subprocess.Popen(
            ["node", str(executable), "start", "--hostname", "127.0.0.1", "--port", str(port)],
            cwd=ROOT / "web", env=env, stdout=log, stderr=subprocess.STDOUT,
        )
        try:
            deadline = time.monotonic() + 30
            while True:
                if web.poll() is not None:
                    raise RuntimeError("web server exited during startup")
                try:
                    with urllib.request.urlopen(env["SAT_SA_BASE_URL"] + "/login", timeout=2):
                        break
                except OSError:
                    if time.monotonic() >= deadline:
                        raise RuntimeError("web server did not become ready")
                    time.sleep(0.5)
            subprocess.run(
                ["node", "--test", "tests/sat-sa-ui.test.mjs"],
                cwd=ROOT / "web", env=env, check=True,
            )
        finally:
            _stop_processes(web)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--port", type=int, default=8877)
    parser.add_argument("--web", action="store_true")
    parser.add_argument("--web-port", type=int, default=3177)
    args = parser.parse_args(argv)
    # This rehearsal explicitly tests the no-provider path.
    os.environ["SATSA_LLM_CHAIN"] = "[]"
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="closure-trace-rehearsal-") as scratch:
        data = Path(scratch)
        api_process, worker, credentials = start(data, args.port, seed_demo=False)
        try:
            base, org = credentials["api"], credentials["organization_id"]
            analyst = Api(base, credentials["analyst"], org)
            runs = seed(analyst, mode="graph")
            wait(analyst, runs, 300)
            entities = {e["id"]: e["display_name"] for e in analyst.all("/api/v1/entities")}
            primary = next(r for r in runs if entities[analyst.call(
                "GET", f"/api/v1/runs/{r}")["entity_id"]] == "CSE-EXEC")
            findings = analyst.all(f"/api/v1/runs/{primary}/findings")
            briefing = analyst.call("GET", f"/api/v1/runs/{primary}/briefing")
            if briefing["status"] != "deterministic":
                raise RuntimeError("no-provider briefing was not deterministic")
            supervisor = Api(base, credentials["supervisor"], org)
            supervisor.call("POST", f"/api/v1/runs/{primary}/decision", body={
                "action": "confirm",
                "reason": "Synthetic rehearsal: reviewed cited premature-closure and escalation-gap evidence.",
            })
            deadline = time.monotonic() + 120
            while True:
                status = supervisor.call("GET", f"/api/v1/runs/{primary}")["status"]
                if status in {"completed", "partial"}:
                    break
                if status in {"failed", "cancelled"} or time.monotonic() >= deadline:
                    raise RuntimeError(f"finalization did not complete: {status}")
                time.sleep(0.5)
            verified = supervisor.call("POST", f"/api/v1/runs/{primary}/verify")
            if verified["status"] != "verified":
                raise RuntimeError("original decided state did not verify")
            receipt = supervisor.call("GET", f"/api/v1/runs/{primary}/receipt")
            tamper = tamper_check(supervisor, data, primary, receipt)
            if args.web:
                web_smoke(data, base, args.web_port)
            print(json.dumps({
                "result": "CLOSURE-TRACE REHEARSAL PASSED",
                "data": "synthetic, disposable local database",
                "entities": len(entities), "runs": len(runs), "primary": "CSE-EXEC",
                "primary_signal_findings": sum(f["state"] == "signal" for f in findings),
                "briefing": briefing["status"], "human_decision": "confirm",
                "verification": verified["status"], "algorithm": receipt["algorithm_id"],
                "tamper": tamper, "web_smoke": "passed" if args.web else "not requested",
                "elapsed_seconds": round(time.monotonic() - started, 2),
            }, indent=2))
        finally:
            _stop_processes(worker, api_process)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
