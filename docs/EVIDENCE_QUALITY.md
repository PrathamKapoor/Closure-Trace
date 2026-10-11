# Evidence Quality Assurance Architecture

## Overview

The Evidence Quality Assurance subsystem in Closure-Trace addresses the documented gap where valid individual CSV/JSON rows can nonetheless describe an unreliable review scope or invalid analytical inputs.

## Detected Defect Classes

The `EvidenceQualityWorker` evaluates incoming datasets for four distinct classes of data reliability issues:

### 1. Out-of-Period Evidence (`evidence_quality.out_of_period`)
- **Violated Condition**: Record `created_at` or `opened_at` timestamps fall outside the declared assessment window `[period_start, period_end]`.
- **Why It Matters**: Injecting historical or future events skews rate-based statistics, moving medians, and baseline thresholds, leading to false alerts.
- **Ingestion vs Analytics Policy**: Ingestion emits non-fatal warnings and preserves raw provenance; the analytics worker emits qualified findings pointing to the specific offending native IDs.
- **Recommended Action**: `REQUEST_MISSING_EVIDENCE` (requesting aligned submission slice).

### 2. Chronological Lifecycle Inversions (`evidence_quality.chronology_violation`)
- **Violated Condition**: 
  - Alert `closed_at < acknowledged_at` or `acknowledged_at < created_at`.
  - Case `closed_at < opened_at`.
  - Investigation steps executed before case opening or in inverted sequence numbers.
- **Why It Matters**: Indicates corrupt upstream clock synchronization or manipulated log exports designed to simulate fast closure metrics.
- **Recommended Action**: `INSPECT_INVESTIGATION` (auditing timestamps and analyst notes).

### 3. Contradictory Dispositions (`evidence_quality.contradictory_dispositions`)
- **Violated Condition**: The same alert or case receives mutually irreconcilable outcomes across multiple records (e.g., both `true_positive` and `benign`).
- **Why It Matters**: Directly compromises supervisory certainty. Reviewers cannot trust downstream automated actions when final categorization is ambiguous.
- **Recommended Action**: `INSPECT_ROOT_CAUSE_REMEDIATION` (reconciling conflicting determinations).

### 4. Incompatible Workflow States (`evidence_quality.incompatible_workflow_states`)
- **Violated Condition**: A Case is marked `closed` while linked Alerts remain open without terminal closure timestamps.
- **Why It Matters**: Indicates an unmanaged residual risk where cases are checked off without resolving actual security alerts.
- **Recommended Action**: `INSPECT_INVESTIGATION` (confirming unclosed child alerts).

## Evaluation

Evidence Quality checks are validated through:
- Unit tests: `tests/test_satsa_evidence_quality.py`
- Controlled Supervisory Benchmark v1.1.0: Scenario `conflicting-evidence` (Scenario 6 in `satsa/analysis/compval.py`), achieving 100% detection recall and expected supervisory action alignment (`SATSA_INSPECT`).
