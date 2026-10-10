# Changelog

Changes are grouped by capability. Earlier implementation details and measured
limitations are preserved in [engineering notes](docs/IMPLEMENTATION_NOTES.md)
and [verification claims](docs/CLAIMS.md). Historical verification results apply
to their cited commits; they do not substitute for checks on the current release.

## Unreleased

### Repository and documentation

- Publish Closure-Trace for the ForgeHacks AI + Cybersecurity track, retaining
  the SAT-SA / TRUST-SAT implementation and Git history.
- Provide fresh-clone setup, configuration templates, and local database
  initialization instructions. Provider credentials are supplied by each user.
- Organize documentation and tests by capability, with descriptive filenames,
  updated imports and CI commands, and a public `satsa` version of `0.16.0`.
- Keep local trust keys, environment files, logs, databases, and generated HSM
  diagnostics out of tracking.

### Application capabilities

- Ingest versioned security submissions and run tenant-scoped, asynchronous
  analysis through the API and independent worker.
- Review findings, evidence, risk, recommendations, and recorded decisions
  through the Next.js workbench or the standalone local dashboard.
- Verify evidence provenance and review records with ML-DSA-65 signatures,
  canonical digests, and append-only ledgers.
- Manage advisory model artifacts and review-outcome training through the
  MLOps lifecycle. Optional provider-assisted briefings fall back to
  deterministic summaries when unavailable or unconfigured.
- Support PostgreSQL and private object storage for hosted deployments,
  with SQLite and local storage for the local demo.

### Evaluation and hardening

- Provide seeded synthetic supervisory scenarios, statistical baselines,
  prioritization experiments, per-worker ablation, and provenance checks.
- Include controlled CIC-IDS2017/BOTS adapters and workflow augmentation;
  adapter validation on sample rows is not validation against real SOC work.
- Provide package-integrity checks, an offline installation rehearsal tool,
  authentication and tenant-isolation tests, and adversarial trust checks.
- Preserve measured results in [benchmark results](reports/CONTROLLED_BENCHMARK_RESULTS.md).
  These are synthetic measurements, with their original limitations retained.

## Validation boundaries

Synthetic tests demonstrate implementation mechanics. They do not establish
real-world detection accuracy, expert validation, or analyst time savings.
Hosted deployment history describes the inherited TRUST-SAT deployment;
Closure-Trace has no separately verified public deployment.
