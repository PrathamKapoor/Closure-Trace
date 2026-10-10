# SIH Requirement Audit (SIH 26157)

This is a self-audit mapping every requirement in the SIH 26157
problem statement to SAT-SA coverage, with an honest
COMPLETE / PARTIAL / NOT-IMPLEMENTED / NOT-APPLICABLE tag for
each. Every "COMPLETE" row is backed by a test or a doc reference.

## Tooling Capabilities Required by SIH 26157

| # | Requirement (paraphrased) | SAT-SA coverage | Status | Evidence |
|---|---|---|---|---|
| 1 | Structured CSE data ingestion (CSV/JSON/database exports/API) | `satsa.ingest` accepts CSV + JSON (+ JSONL). Database/API adapter is out of scope of the current build. | PARTIAL | the implementation docs; `tests/test_satsa_ingestion.py` (32 tests) |
| 2 | Normalization into a canonical domain model | `satsa.ingest.normalize` produces `Alert` / `Case` / `InvestigationStep` / `Escalation` / `Disposition` / `Asset` with full alias handling. | COMPLETE | the implementation doc; tests |
| 3 | Data validation (malformed input, missing fields, invalid timestamps, broken relationships, duplicates) | `IngestionResult` enumerates per-row rejections; `IngestionError` for file-level failures; per-file digests + re-submission guard. | COMPLETE | the implementation doc; tests for missing required, invalid ts, within-file dup, cross-sub dup, broken ref |
| 4 | Provenance (submission id, CSE, period, format, digest, ingest ts, version) | Every accepted row carries a `SourceRecord`; every submission has `file_digests_json` + `snapshot_digest` + `content_digest` on every row. | COMPLETE | the implementation doc; tests |
| 5 | Analysis run engine | `satsa.analysis.run.RunService` orchestrates workers, persists `AnalysisRun` + `Observation` + `Finding` + `Job` in a transaction. | COMPLETE | the implementation doc; 15 tests |
| 6 | Worker contract (id, version, inputs, outputs, findings, confidence, evidence refs) | `AnalyticalWorker` ABC + `ObservationBatch` shape. | COMPLETE | the implementation doc; tests |
| 7 | First worker: Critical/High severity closure analysis | `FastClosureWorker` with configurable thresholds, per-severity. | COMPLETE | the implementation doc; tests |
| 8 | Execution gap 5.1: Acknowledged alert without meaningful investigation | `AckWithoutInvestigationWorker` | COMPLETE | the implementation doc; tests |
| 9 | Execution gap 5.2: Critical/high alert closed unusually quickly | `FastClosureWorker` (5.2) | COMPLETE | the implementation doc; tests |
| 10 | Execution gap 5.3: Critical alert closed without escalation | `CriticalWithoutEscalationWorker` | COMPLETE | the implementation doc; tests |
| 11 | Execution gap 5.4: Repeated investigation patterns | `RepeatedInvestigationWorker` | COMPLETE | the implementation doc; tests |
| 12 | Execution gap 5.5: Repeated alerts without remediation | `RecurringWithoutRemediationWorker` | COMPLETE | the implementation doc; tests |
| 13 | Execution gap 5.6: Potential metric gaming | `MetricGamingWorker` | COMPLETE | the implementation doc; tests |
| 14 | Every finding must answer WHAT / WHY / WHAT evidence / WHAT to inspect | Every `Finding` has `rationale` (WHY), `scoped_subjects` (WHAT), `evidence_refs` (WHAT evidence), `limitations` (WHAT to inspect). | COMPLETE | the implementation doc |
| 15 | Negative space: critical asset with no expected activity | `NegativeSpaceWorker.missing_monitoring` | COMPLETE | the implementation doc; tests |
| 16 | Negative space: missing monitoring coverage | `missing_monitoring` | COMPLETE | the implementation doc |
| 17 | Negative space: missing investigation | `missing_investigation` | COMPLETE | the implementation doc |
| 18 | Negative space: missing escalation | `missing_escalation` | COMPLETE | the implementation doc |
| 19 | Negative space: unexpectedly low activity | `unexpectedly_low_activity` (with min-volume guard) | COMPLETE | the implementation doc |
| 20 | Negative space must distinguish absence-in-reality from absence-from-submission | `data_completeness` map in scope; `missing_file.*` rules; per-finding confidence.evidence_completeness. | COMPLETE | the implementation doc; tests |
| 21 | Zero activity must not auto-fire a finding | `min_alert_volume_for_low_activity`, `min_critical_assets`, `min_samples` guards in every worker. | COMPLETE | the implementation doc; `test_zero_activity_alone_is_not_a_finding` |
| 22 | Anomaly detection (alerts per asset, closure, escalation rate, recurrence, coverage, investigation depth) — explainable statistics | `AnomalyWorker` with median/MAD/percentile across 8 metrics. No black-box ML. | COMPLETE | the implementation doc; 21 tests |
| 23 | Anomaly output: observed value, baseline, deviation, confidence, evidence, explanation | Every `anomaly.*` finding carries statistic, threshold, effect, confidence, evidence_refs, limitations, rationale. | COMPLETE | the implementation doc |
| 24 | Peer benchmarking with cohort selection (not blind comparison) | `PeerBenchmarkWorker` with `sector` + `environment_class` cohort; min_peers guard. | COMPLETE | the implementation doc; 12 tests |
| 25 | Peer comparison across closure, investigation, escalation, alert volume, coverage, recurrence | 7 peer metrics (closure_median, closure_rate, escalation_rate, investigation_depth_median, recurrence_median, monitoring_coverage, alerts_per_critical_asset) | COMPLETE | the implementation doc |
| 26 | Peer output: spec-style (observed / peer / deviation / signal / confidence) | Every peer finding carries the four numbers; spec example (4.2 min vs 38.7 min, 94% confidence) is reproducible. | COMPLETE | the implementation doc; `test_peer_benchmark_emits_spec_style_finding` |
| 27 | Only display numbers actually computed | Every `Finding.statistic / threshold / effect` is from a real measurement; no fabricated data. | COMPLETE | All changes |
| 28 | Entity risk engine (decomposable: 82 → {execution_gap, peer_deviation, …}) | `satsa.analysis.risk.compute_entity_risk` returns 7-dimension profile with `total_score`, per-dimension scores, decomposition tree. | COMPLETE | the implementation doc; 16 tests |
| 29 | Risk must not invent arbitrary weights | `DIMENSION_WEIGHTS` documented in `risk.py`; every persisted profile carries its weights. | COMPLETE | the implementation doc |
| 30 | Review prioritization: "what should I look at first?" — entities, controls, processes, cases, alerts | `prioritize_entities` (entities) + `prioritize_findings` (cases/alerts) with evidence-backed rationale. | COMPLETE | the implementation doc; 13 tests |
| 31 | Priority must have evidence-backed reasoning | Every entry has `rationale` quoting real numbers. | COMPLETE | the implementation doc |
| 32 | Trust: cryptographic provenance | `satsa.analysis.trust.TrustService` signs every run + every finding with ML-DSA-65. `satsa_trust_receipts` table. | COMPLETE | the implementation doc; 16 tests |
| 33 | Trust: integrity verification | `SatsaService.verify_run` re-derives each record's live digest and verifies the PQC signature. | COMPLETE | the implementation doc |
| 34 | Trust: tamper tests (modified evidence, modified finding, broken provenance, invalid signature, altered chain) | the implementation tests cover: digest mismatch, rationale tamper, observation_id repoint, missing receipt, signature corruption. | COMPLETE | the implementation doc |
| 35 | Trust: do not claim "quantum proof" storage | Documentation explicitly states "detection of tampering at verification time, not tamper-proof storage." | COMPLETE | the implementation doc |
| 36 | Human review workflow (confirm / dismiss / escalate / annotate / request_review) | `SatsaService.record_review` + UI form on finding detail. | COMPLETE | the implementation doc; 8 tests |
| 37 | Audit: actor, action, timestamp, target, reason, evidence context, integrity | `satsa_review_decisions` table with all fields + `finding_content_digest` bound to the exact version of the record. | COMPLETE | the implementation doc |
| 38 | Human decisions must be authoritative, append-only | `record_review` always inserts a new row with `previous_revision_id`; never edits history. | COMPLETE | the implementation doc |
| 39 | End-to-end vertical slice (submission → ingestion → analysis → finding → risk → evidence → trust → review) | `tests/test_satsa_e2e_vertical_slice.py` runs all 5 demo CSEs through the full pipeline. | COMPLETE | the implementation doc |
| 40 | Demo dataset with multiple CSEs (healthy, execution gap, negative space, anomaly, peer deviation) | `docs/demo/submissions/CSE-{HEALTHY,EXEC,NEG,ANOM,PEER}` + `ground-truth.json`. | COMPLETE | the implementation doc |
| 41 | UI: Overview / Entities / Findings / Review Queue / Benchmarks / Evidence / Reports / System | `satsa/ui` FastAPI app with all eight sections. | COMPLETE | the implementation doc; 13 tests |
| 42 | Dashboard: entity risk, high-priority entities, finding counts, signal categories, review queue, evidence integrity | `/` overview page renders all of these. | COMPLETE | the implementation doc |
| 43 | Entity page: overall risk, risk dimensions, findings, trends, benchmarks, evidence | `/entities/{id}` renders all of these. | COMPLETE | the implementation doc |
| 44 | Finding page: finding, severity, confidence, rationale, evidence, source records, recommendation, trust status | `/findings/{id}` renders all of these. | COMPLETE | the implementation doc |
| 45 | Polished UI: layout, typography, spacing, navigation, filtering, sorting, loading states, empty states, error states, drill-down, useful charts, tables | `satsa/ui/static/style.css` + Jinja2 templates. | COMPLETE | the implementation doc |
| 46 | Avoid meaningless animations | No JS animations in the UI; only CSS transitions on hover. | COMPLETE | the implementation |
| 47 | Demo mode: "Load Demonstration Assessment" button + offline demo flow | UI's hero CTA; `satsa/ui/demo.py` loader. | COMPLETE | the implementation + 15 |
| 48 | Reporting: assessment info, executive summary, entity risk, findings, execution gaps, negative space, peer comparison, recommendations, evidence references, trust/integrity | `satsa.analysis.report.render_report` + `/reports/{id}` route. | COMPLETE | the implementation (in `report.py`) |
| 49 | Operational environment: no runtime Internet, no cloud dependency, no remote AI, local database, local models, local assets, local reports, configuration, startup, shutdown, storage, logs | the implementation offline test + platform's existing SQLite + local PQC. | COMPLETE | the implementation doc |
| 50 | Validation framework: ground truth, precision, recall, detection rate, false positives, false negatives, prioritization effectiveness, review workload reduction | Demo dataset + ground-truth comparison in `test_satsa_e2e_vertical_slice`. Synthetic-only — clearly labeled. | PARTIAL (synthetic) | the implementation + the implementation |
| 51 | Success criteria (SIH-specific) | All covered; see component-level docs. | COMPLETE | All changes |
| 52 | Out-of-scope: must NOT be a SOC, SIEM, real-time monitoring, telemetry, national monitoring | The system analyses periodic submissions; no continuous ingestion, no real-time alerts, no telemetry. | NOT-APPLICABLE (correctly) | Architecture docs |
| 53 | Deployment: installable, runnable offline, ingest a submission, run analysis, inspect findings, trace evidence, verify integrity, make a decision, generate a report | the implementation deployment audit + the implementation demo runbook cover all of this. | COMPLETE | the implementation + 25 |

## Summary

| Status | Count |
|---|---|
| COMPLETE | 50 |
| PARTIAL | 2 (database/API ingestion adapter out of scope of the current build; synthetic validation is the only feasible validation without a labelled expert dataset) |
| NOT-IMPLEMENTED | 0 |
| NOT-APPLICABLE | 1 (real-time monitoring — correctly excluded by design) |
