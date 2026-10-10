# Agent Inventory

The registry contains 32 components: 9 MLOps components and 23 supervisory
components. The tables identify each component's runtime role, implementation,
and supporting tests. A registry entry alone does not imply a running agent.

Correlation and signal fusion are distinct from entity risk scoring: the
former groups corroborating findings, while the latter computes risk dimensions.
The existing `satsa.fusion` identifier remains stable for compatibility.

Categories used below:

- **runtime (orchestrated)** — has real, tested implementation code,
  and the SAT-SA `SupervisorEngine` / `RunService` actually invokes it
  as part of a run.
- **runtime (standalone)** — has real, tested implementation code
  (verified: not a stub — see LOC/test counts), but is not invoked
  through the SAT-SA supervisor's own `observe()` call path; it runs
  under the separate `qsmlops` MLOps pipeline instead.
- **specification** — a registered `AgentSpec` entry (id, purpose,
  inputs/outputs/evidence contract) with a real `implementation_ref`,
  used by the agent-explorer UI and the supervisor's routing table.
  Every agent in this registry has this; it is not itself a runtime
  vs. non-runtime distinction, so it is not repeated as a column below
  — see the "Runtime" column instead.

## 23 SAT-SA supervisory agents — all runtime (orchestrated)

Every one of these is invoked by `satsa.analysis.run.RunService` (the
16-worker default set), directly by `satsa.analysis.risk.compute_entity_risk`
(the correlation step), or by `satsa.supervisor.engine.SupervisorEngine`,
backed by real, tested code — not specs standing in for unimplemented
logic. Five are new at the time of the recorded verification, one more at the time of the recorded verification (marked
below).

| Agent | Runtime | Implementation | Representative tests |
|---|---|---|---|
| Entity & Asset Resolution ** | orchestrated | `satsa/analysis/workers/entity_asset_resolution.py` | `test_satsa_entity_asset_resolution.py` (7) |
| Ingestion | orchestrated | `satsa/ingest/service.py` | `test_satsa_ingestion.py` (32), `test_satsa_partial_ref_resolution.py` (4) |
| Normalization | orchestrated | `satsa/ingest/normalize.py` | `test_satsa_ingestion.py`, `test_satsa_partial_ref_resolution.py` |
| Execution Gap | orchestrated | `satsa/analysis/workers/` (6 detector modules) | `test_satsa_execution_gaps.py` |
| Negative Space | orchestrated | `satsa/analysis/workers/negative_space.py` | `test_satsa_negative_space.py` (23, incl. the existing escalation-logic fix) |
| Workflow Reconstruction ** | orchestrated | `satsa/analysis/workers/workflow_reconstruction.py` | `test_satsa_workflow_reconstruction.py` (12) |
| Anomaly | orchestrated | `satsa/analysis/workers/anomaly.py` | `test_satsa_anomaly.py` |
| Peer Benchmark | orchestrated | `satsa/analysis/workers/peer_benchmark.py` | `test_satsa_peer_benchmark.py`, `test_satsa_peer_robust.py`, `test_satsa_peer_robustness.py` |
| Coverage Gap | orchestrated | `satsa/analysis/workers/coverage_gap.py` | `test_satsa_new_workers.py` |
| Drift | orchestrated | `satsa/analysis/workers/drift.py` | `test_satsa_drift.py`, `test_cross_period_cross_entity_wiring.py` |
| Cross-Entity Insights | orchestrated | `satsa/analysis/workers/cross_entity_insights.py` | `test_satsa_insights.py`, `test_cross_period_cross_entity_wiring.py` |
| Case Similarity | orchestrated | `satsa/analysis/case_similarity.py` | `test_satsa_case_similarity.py` |
| Evidence Completeness | orchestrated | `satsa/analysis/workers/evidence_completeness.py` | `test_satsa_new_workers.py` |
| Correlation & Signal Fusion ** | orchestrated (runs inside `compute_entity_risk`, ahead of dimension scoring) | `satsa/analysis/correlation.py` | `test_satsa_correlation_fusion.py` (12) |
| Entity Risk Scoring (formerly "Fusion") | orchestrated | `satsa/analysis/risk.py` | `test_satsa_entity_risk.py` |
| Prioritization | orchestrated | `satsa/analysis/prioritize.py` | `test_satsa_prioritize.py`, `test_adaptive_supervisor.py` |
| Recommendation | orchestrated | `satsa/analysis/recommend.py` | exercised across `test_satsa_auth_rbac.py`, `test_satsa_fresh_database_e2e.py`, `test_satsa_tamper_matrix.py` |
| Review Workflow | orchestrated | `satsa/analysis/review.py` | `test_satsa_review.py`, `test_satsa_review_analytics.py`, `test_satsa_auth_rbac.py`, `test_satsa_tamper_matrix.py` |
| Trust-Provenance | orchestrated | `satsa/analysis/trust.py` | `test_satsa_trust.py`, `test_satsa_trust_determinism.py, test_satsa_trust_adversarial.py`, `test_satsa_trust_stress.py`, `test_satsa_tamper_matrix.py` |
| Evidence & Explainability Assembly ** | orchestrated (called by the UI's `/findings/{id}` route, not a parallel unused module) | `satsa/analysis/evidence_assembly.py` | `test_satsa_evidence_assembly.py` (9) |
| Supervisory Audit & Compliance / Meta-Audit ** | orchestrated (database-wide sweep, `sat-sa audit` CLI) | `satsa/analysis/meta_audit.py` | `test_satsa_meta_audit.py` (6) |
| Supervisory Report Generation *(the implementation — newly registered)* | orchestrated | `satsa/analysis/report.py` | `test_satsa_e2e_vertical_slice.py` and others (real code that predates the implementation; only the registry entry is new) |
| Validation | orchestrated | `satsa/analysis/validate.py`, `compval.py` | `test_satsa_synth.py`, `test_satsa_composition_validation.py`, `test_satsa_expert_validation.py` |

## 9 retained MLOps agents — runtime (standalone), not SAT-SA-orchestrated

These are **not** decorative registry entries — each has a real,
substantial implementation (`qsmlops/agents/*.py`, ~1,600 lines
combined, none of them stubs) with its own test coverage under the
qsmlops test suite. What "retained" precisely means: SAT-SA's own
`SupervisorEngine` does not call into these — they run under the
separate qsmlops MLOps pipeline, governing the ML platform itself
(dataset integrity, model performance, deployment governance), not
SOC/CSE supervisory analytics. They appear in the 32-agent registry as
`AgentSpec` entries so the architecture diagram and agent explorer
represent the *whole* platform truthfully, not because SAT-SA calls
their `observe()` method.

| Agent | Runtime | Implementation | Notes |
|---|---|---|---|
| Data Agent | standalone (qsmlops pipeline) | `qsmlops/agents/data_agent.py` | Dataset integrity, artifact hashing |
| Performance Agent | standalone | `qsmlops/agents/performance_agent.py` | ML metric evaluation vs. rolling baseline |
| Security Agent | standalone | `qsmlops/agents/security_agent.py` | Dependency CVE scanning, artifact integrity |
| Quantum Security Agent | standalone | `qsmlops/agents/quantum_agent.py` | Cryptographic posture (the same PQC stack SAT-SA's TRUST-SAT reuses) |
| Red Team Agent | standalone | `qsmlops/agents/redteam.py` | Byte-tamper tripwire, provenance, perturbation testing |
| Training Optimization Agent | standalone | `qsmlops/agents/training_optimization_agent.py` | Sample/feature/seed adequacy heuristics |
| Incident Response Agent | standalone | `qsmlops/agents/incident_response_agent.py` | Model-state denial/critical/repetition analysis |
| Governance Agent | standalone | `qsmlops/agents/governance_agent.py` | Model-state compliance, registry hygiene |
| Optimization Agent | standalone | `qsmlops/agents/optimization_agent.py` | Storage/registry hygiene |

## Summary

- 32 total (9 + 23), matching the roadmap's stated architecture as of
  This revision.
- **All 32 have real, executable, tested implementation code** — none
  is a bare placeholder or documentation-only entry.
- The honest nuance the "32 agents" framing needs stated plainly: the
  23 SAT-SA agents are orchestrated together by one engine on one
  supervisory data path; the 9 MLOps agents are orchestrated together
  by a separate engine on a separate (ML-platform) data path. They
  coexist in one repository and one registry, not one call graph.
  Anyone auditing "does SAT-SA's analysis of a CSE submission actually
  invoke 32 agents" should get the honest answer: 23, plus 9 more that
  govern the platform the SAT-SA code itself runs on.
- Three of the 23 (Correlation & Signal Fusion, Evidence &
  Explainability Assembly, Meta-Audit) are invoked outside the main
  16-worker `RunService` pipeline — one from inside
  `compute_entity_risk` ahead of dimension scoring, one from the UI's
  finding-detail route, one from the `sat-sa audit` CLI command and a
  database-wide sweep. They are still real, orchestrated, tested code
  with a registered `AgentSpec`, not specifications standing in for
  unbuilt logic; the "orchestrated" column notes exactly how each is
  invoked so this distinction isn't hidden.
