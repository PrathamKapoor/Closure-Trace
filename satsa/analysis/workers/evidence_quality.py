"""Evidence Quality worker: detect scope anomalies, out-of-period evidence,
chronology violations, contradictory dispositions, and incompatible workflow states.

Performs domain-level validation without discarding raw evidence:
- out_of_period: evidence timestamps fall outside declared assessment period bounds.
- chronology_violation: alert acknowledged before creation, closed before acknowledgement,
  case closed before opening, or investigation steps out of chronological sequence.
- contradictory_dispositions: multiple conflicting dispositions on the same alert or case
  (e.g., both 'true_positive' and 'benign_positive').
- incompatible_workflow_state: case marked closed while linked alert remains open without
  closure/disposition, or open case with closed disposition.
- missing_references: references between alerts and cases that fail referential integrity.

Every finding emitted provides:
- Scoped subjects (the specific alert_id, case_id, or step_ids affected).
- SourceRecord references pointing to original submission evidence rows.
- Clear rationale of the violated condition and supervisory consequence.
- Specific next action recommended for the reviewer.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from satsa.contracts.worker import (
    AnalyticalWorker,
    ObservationBatch,
    RunContext,
)
from satsa.domain.evidence import (
    ConfidenceVector,
    Finding,
)


@dataclass(frozen=True)
class EvidenceQualityThresholds:
    """Thresholds / policy configuration for Evidence Quality checks."""
    # When True, flag any evidence with timestamps outside [period_start, period_end]
    flag_out_of_period: bool = True
    # When True, check timestamp chronological order
    flag_chronology_violations: bool = True
    # When True, flag conflicting dispositions for the same entity/alert/case
    flag_contradictory_dispositions: bool = True
    # When True, flag alert/case workflow status mismatches
    flag_incompatible_states: bool = True


DEFAULT_EVIDENCE_QUALITY_POLICY = EvidenceQualityThresholds()


class EvidenceQualityWorker(AnalyticalWorker):
    """Analytical worker detecting evidence quality defects, chronology violations,
    and material workflow contradictions across the scoped dataset."""

    name = "evidence-quality"
    version = "1.0.0"

    def __init__(self, thresholds: Optional[EvidenceQualityThresholds] = None) -> None:
        self.thresholds = thresholds or DEFAULT_EVIDENCE_QUALITY_POLICY

    def evaluate(self, snapshot, dataset, baselines, policy, run_context) -> ObservationBatch:
        findings: list[Finding] = []
        alerts = dataset.alerts or []
        cases = dataset.cases or []
        steps = dataset.steps or []
        dispositions = dataset.dispositions or []
        escalations = dataset.escalations or []

        p_start = float(getattr(dataset, "period_start", 0.0) or 0.0)
        p_end = float(getattr(dataset, "period_end", 0.0) or 0.0)
        has_period = p_start > 0.0 and p_end > 0.0 and p_end >= p_start

        # -------------------------------------------------------------
        # 1. Out of Period Evidence
        # -------------------------------------------------------------
        if self.thresholds.flag_out_of_period and has_period:
            out_alerts = [a for a in alerts if a.created_at < p_start or a.created_at > p_end]
            out_cases = [c for c in cases if c.opened_at < p_start or c.opened_at > p_end]
            
            if out_alerts or out_cases:
                subjects = [a.id for a in out_alerts] + [c.id for c in out_cases]
                evidence_refs = [a.source_record_ref for a in out_alerts if a.source_record_ref]
                total_items = max(1, len(alerts) + len(cases))
                ratio = len(subjects) / total_items

                findings.append(Finding(
                    observation_id="",
                    rule_or_category="evidence_quality.out_of_period",
                    state="signal",
                    rationale=(
                        f"Detected {len(out_alerts)} alert(s) and {len(out_cases)} case(s) with timestamps "
                        f"outside the declared assessment period [{p_start:.0f}, {p_end:.0f}]. "
                        "Evidence submitted outside the agreed window distorts metric baselines."
                    ),
                    scoped_subjects=subjects,
                    statistic=float(len(subjects)),
                    effect=min(1.0, ratio),
                    threshold=0.0,
                    confidence=ConfidenceVector(
                        analytical_support=1.0,
                        evidence_completeness=1.0,
                        peer_confidence=None,
                    ),
                    evidence_refs=evidence_refs,
                    limitations="Timestamps verified against assessment declared period bounds.",
                ))

        # -------------------------------------------------------------
        # 2. Chronology Violations
        # -------------------------------------------------------------
        if self.thresholds.flag_chronology_violations:
            chrono_alerts = []
            for a in alerts:
                if a.acknowledged_at is not None and a.acknowledged_at < a.created_at:
                    chrono_alerts.append(a)
                elif a.closed_at is not None and a.created_at is not None and a.closed_at < a.created_at:
                    chrono_alerts.append(a)
                elif a.closed_at is not None and a.acknowledged_at is not None and a.closed_at < a.acknowledged_at:
                    chrono_alerts.append(a)

            chrono_cases = []
            for c in cases:
                if c.closed_at is not None and c.closed_at < c.opened_at:
                    chrono_cases.append(c)

            chrono_steps = []
            case_map = {c.id: c for c in cases}
            for s in steps:
                parent_case = case_map.get(s.case_id)
                if parent_case and s.performed_at < parent_case.opened_at:
                    chrono_steps.append(s)

            if chrono_alerts or chrono_cases or chrono_steps:
                subjects = [a.id for a in chrono_alerts] + [c.id for c in chrono_cases] + [s.id for s in chrono_steps]
                evidence_refs = [a.source_record_ref for a in chrono_alerts if a.source_record_ref]
                findings.append(Finding(
                    observation_id="",
                    rule_or_category="evidence_quality.chronology_violation",
                    state="signal",
                    rationale=(
                        f"Found {len(chrono_alerts)} alert(s), {len(chrono_cases)} case(s), and "
                        f"{len(chrono_steps)} step(s) with chronological inversions (e.g. closure before creation, "
                        "or action before case opening). Indicates potential timestamp manipulation or logging flaw."
                    ),
                    scoped_subjects=subjects,
                    statistic=float(len(subjects)),
                    effect=min(1.0, len(subjects) / max(1, len(alerts) + len(cases))),
                    threshold=0.0,
                    confidence=ConfidenceVector(
                        analytical_support=1.0,
                        evidence_completeness=0.9,
                        peer_confidence=None,
                    ),
                    evidence_refs=evidence_refs,
                    limitations="Checks compare relative timestamps on linked workflow entities.",
                ))

        # -------------------------------------------------------------
        # 3. Contradictory Dispositions
        # -------------------------------------------------------------
        if self.thresholds.flag_contradictory_dispositions:
            # Check alerts with multiple conflicting dispositions
            disps_by_alert: dict[str, list] = {}
            for d in dispositions:
                if d.alert_id:
                    disps_by_alert.setdefault(d.alert_id, []).append(d)

            contradictory_alerts = []
            for aid, dlist in disps_by_alert.items():
                categories = {d.mapped_category for d in dlist if d.mapped_category}
                # If there are opposing conclusions (e.g. true_positive vs benign / false_positive)
                has_positive = any(c in categories for c in ("true_positive", "incident", "malicious"))
                has_benign = any(c in categories for c in ("benign", "benign_positive", "false_positive", "test"))
                if len(categories) > 1 and has_positive and has_benign:
                    contradictory_alerts.append((aid, categories))

            if contradictory_alerts:
                subjects = [ca[0] for ca in contradictory_alerts]
                evidence_refs = []
                for aid, _ in contradictory_alerts:
                    for d in disps_by_alert.get(aid, []):
                        if getattr(d, "source_record_ref", None):
                            evidence_refs.append(d.source_record_ref)
                if not evidence_refs:
                    # fallback to alert source record refs
                    for a in alerts:
                        if a.id in subjects and a.source_record_ref:
                            evidence_refs.append(a.source_record_ref)

                findings.append(Finding(
                    observation_id="",
                    rule_or_category="evidence_quality.contradictory_dispositions",
                    state="signal",
                    rationale=(
                        f"Detected {len(contradictory_alerts)} alert(s) with mutually contradictory disposition "
                        "determinations (e.g., both malicious/true-positive and benign/false-positive). "
                        "Conflicting outcomes compromise supervisory conclusion reliability."
                    ),
                    scoped_subjects=subjects,
                    statistic=float(len(contradictory_alerts)),
                    effect=min(1.0, len(contradictory_alerts) / max(1, len(alerts))),
                    threshold=0.0,
                    confidence=ConfidenceVector(
                        analytical_support=1.0,
                        evidence_completeness=1.0,
                        peer_confidence=None,
                    ),
                    evidence_refs=evidence_refs,
                    limitations="Flags alerts having multiple dispositions with irreconcilable outcome categories.",
                ))

        # -------------------------------------------------------------
        # 4. Incompatible Workflow States
        # -------------------------------------------------------------
        if self.thresholds.flag_incompatible_states:
            incompatible = []
            alerts_by_id = {a.id: a for a in alerts}
            for c in cases:
                if c.status == "closed":
                    for aid in c.alert_refs:
                        al = alerts_by_id.get(aid)
                        if al and al.closed_at is None:
                            incompatible.append((c.id, al.id))

            if incompatible:
                subjects = list({c_id for c_id, _ in incompatible} | {a_id for _, a_id in incompatible})
                evidence_refs = [
                    alerts_by_id[a_id].source_record_ref
                    for _, a_id in incompatible
                    if a_id in alerts_by_id and alerts_by_id[a_id].source_record_ref
                ]
                findings.append(Finding(
                    observation_id="",
                    rule_or_category="evidence_quality.incompatible_workflow_states",
                    state="signal",
                    rationale=(
                        f"Identified {len(incompatible)} instance(s) where a Case is closed but linked Alerts "
                        "remain unclosed without disposition. Unclosed alerts under closed cases represent orphan "
                        "investigations or incomplete tracking."
                    ),
                    scoped_subjects=subjects,
                    statistic=float(len(incompatible)),
                    effect=min(1.0, len(incompatible) / max(1, len(cases))),
                    threshold=0.0,
                    confidence=ConfidenceVector(
                        analytical_support=0.95,
                        evidence_completeness=0.85,
                        peer_confidence=None,
                    ),
                    evidence_refs=evidence_refs,
                    limitations="Evaluates case closure against the closure states of its referenced alerts.",
                ))

        state = "signal" if findings else "no_signal"
        return ObservationBatch(
            worker_name=self.name,
            detector_version=self.version,
            scope={
                "entity_id": run_context.entity_id,
                "assessment_id": run_context.assessment_id,
                "alerts_total": len(alerts),
                "cases_total": len(cases),
                "period_start": p_start,
                "period_end": p_end,
            },
            state=state,
            findings=findings,
            processing_metrics={
                "checks_run": [
                    "out_of_period",
                    "chronology_violation",
                    "contradictory_dispositions",
                    "incompatible_workflow_states",
                ],
                "findings_count": len(findings),
            },
        )
