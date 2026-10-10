# SAT-SA — Baseline verification

## Git state (start of )

- Branch: `main`, up to date with `origin/main`.
- Commit: `5995f0dab48819bd6fb2588cf4cc55c86861bf91` — identical to the commit the implementation audited; the repository had not changed between changes except for the component's own untracked `docs/design/` files, which were left untouched.
- Working tree: clean except `docs/design/` (untracked, intentional, preserved).

## Baseline test run

Command: `python -m pytest tests -q -ra --junitxml=...`, run in an isolated scratch copy (not the tracked repo) to avoid rewriting the two tracked HSM certification sentinel files (`tests/_a12_artifacts/real_provider_sentinel.txt`, `tests/_a13_artifacts/mldsa_provider_sentinel.txt`) — the implementation used the same precaution for the same reason, and a first attempt at a full-suite run directly in the tracked repo during this component confirmed why: it silently rewrote both sentinel files with degraded results (no `.devtools/softhsm2` DLL in this checkout), which were reverted with `git checkout --`.

Result: **469 collected, 452 passed, 0 failed, 0 errors, 17 skipped, 230.322s.**

This differs from the component's reported 451 passed / 1 failed. The one difference is `tests/test_adaptive_supervisor.py::TestDeterminismAndQuiet::test_adaptive_supervisor_preserves_boundary`, which shells out to `grep` via `subprocess.run(["grep", ...])`. the implementation ran under a shell without `grep` on PATH (PowerShell); this component's Bash tool is Git Bash, which bundles `/usr/bin/grep`. Read directly: the test does a source-tree scan for a stray string (`"guardrailed"`) left over from a historical refactor, unrelated to any the implementation concern. This is a **pre-existing test-portability defect** (the test never checks `subprocess` exit status, so a missing `grep` raises `FileNotFoundError` loudly in one shell and simply runs in another) — not a repository regression, and not something the component's mandate (crypto/identity/persistence/offline/domain/orchestration) covers. It is documented here, left unmodified, and not counted as a the implementation defect.

The 17 skips are unchanged from the implementation: SoftHSM2/PKCS#11 hardware not present in this checkout (`.devtools/softhsm2/lib/*.dll` absent).

## Type checking / lint / build

No `mypy`, `ruff`, or `flake8` installed in this environment (`pip show` returns nothing for all three); no `pyproject.toml` `[tool.mypy]`/`[tool.ruff]` section exists; no CI configuration exists anywhere in the tree (confirmed in this implementation). There is no type-check or lint command to run — this is a genuine tooling gap, not a result being omitted. `python -m py_compile` is not a substitute for real type checking and was not used to manufacture a false "type check passed" signal. There is no separate build step: the package is pure Python, installed via `pip install -e .`; `python -m pytest` succeeding against the installed package is the closest available build-verification signal, and it passed (above).

## Environment

Python 3.13.14 (Windows Store distribution), same machine as the implementation. `pytest` 9.1.1. Package versions unchanged from [the component's technology-baseline.md](../design/technology-baseline.md) table — no dependency was installed, upgraded, or removed during this baseline check.

## Known failures / caveats carried into

- The `grep`-dependent test above is shell-dependent, not fixed (out of scope; noted for a future portability pass).
- SoftHSM2/PKCS#11 hardware path remains untested in this environment (unchanged from the implementation; addressed at the level of "what is required to test it" in [offline-hardening.md](offline-hardening.md), not by installing hardware here).
