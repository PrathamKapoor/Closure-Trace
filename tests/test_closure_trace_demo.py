"""Demo startup must fail honestly and release the processes it started."""

import subprocess
from types import SimpleNamespace

import pytest

from scripts import local_stack, seed_demo_via_api


@pytest.mark.parametrize("status", ["failed", "cancelled", "unexpected"])
def test_failed_demo_analysis_is_not_reported_ready(status):
    api = SimpleNamespace(call=lambda *a: {"status": status})
    with pytest.raises(SystemExit, match=f"ended with {status}"):
        seed_demo_via_api.wait(api, ["demo-run"], 1)


def test_resuming_is_still_processing(monkeypatch):
    statuses = iter(["resuming", "completed"])
    api = SimpleNamespace(call=lambda *a: {"status": next(statuses)})
    monkeypatch.setattr(seed_demo_via_api.time, "sleep", lambda _: None)
    seed_demo_via_api.wait(api, ["demo-run"], 1)


@pytest.mark.parametrize("status", ["awaiting_review", "completed", "partial"])
def test_expected_demo_states_are_accepted(status):
    api = SimpleNamespace(call=lambda *a: {"status": status})
    seed_demo_via_api.wait(api, ["demo-run"], 1)


def test_no_runs_is_not_success():
    with pytest.raises(SystemExit, match="no demo analysis runs"):
        seed_demo_via_api.wait(None, [], 1)


def test_no_dataset_is_not_success(monkeypatch, tmp_path):
    monkeypatch.setattr(seed_demo_via_api, "DEMO_ROOT", tmp_path)
    with pytest.raises(SystemExit, match="no demo submissions"):
        seed_demo_via_api.seed(None, mode="graph")


def test_invalid_demo_submission_stops_setup(monkeypatch, tmp_path):
    (tmp_path / "synthetic").mkdir()
    monkeypatch.setattr(seed_demo_via_api, "DEMO_ROOT", tmp_path)
    calls = []

    def call(method, path, **kwargs):
        calls.append(path)
        if path.endswith("/validation"):
            return {"status": "invalid"}
        return {"id": "synthetic-id", "status": "valid"}

    api = SimpleNamespace(all=lambda _: [], call=call)
    with pytest.raises(SystemExit, match="validation invalid"):
        seed_demo_via_api.seed(api, mode="graph")
    assert "/api/v1/runs" not in calls


class Process:
    def __init__(self):
        self.stopped = False
        self.reaped = False

    def poll(self):
        return None

    def terminate(self):
        self.stopped = True

    def wait(self, timeout):
        self.reaped = True


def test_setup_failure_terminates_api_and_worker(monkeypatch, tmp_path):
    processes = [Process(), Process()]
    monkeypatch.setattr(local_stack, "_run", lambda *a: "")
    monkeypatch.setattr(local_stack.subprocess, "Popen", lambda *a, **kw: processes[0])
    monkeypatch.setattr(local_stack, "_start_worker", lambda *a: processes[1])

    def failed(*a, **kw):
        raise SystemExit("seed refused")

    monkeypatch.setattr(local_stack, "_finish_start", failed)
    with pytest.raises(SystemExit, match="seed refused"):
        local_stack.start(tmp_path, 8877, seed_demo=True)
    assert all(p.stopped and p.reaped for p in processes)


def test_worker_start_failure_reaps_api(monkeypatch, tmp_path):
    process = Process()
    monkeypatch.setattr(local_stack, "_run", lambda *a: "")
    monkeypatch.setattr(local_stack.subprocess, "Popen", lambda *a, **kw: process)

    def failed(*a):
        raise OSError("worker unavailable")

    monkeypatch.setattr(local_stack, "_start_worker", failed)
    with pytest.raises(OSError, match="worker unavailable"):
        local_stack.start(tmp_path, 8877, seed_demo=False)
    assert process.stopped and process.reaped


def test_unresponsive_process_is_killed_after_shutdown_timeout():
    process = Process()
    attempts = []

    def wait(timeout):
        attempts.append(timeout)
        if len(attempts) == 1:
            raise subprocess.TimeoutExpired("worker", timeout)

    process.wait = wait
    process.kill = lambda: setattr(process, "killed", True)
    local_stack._stop_processes(process)
    assert process.stopped and process.killed and len(attempts) == 2
