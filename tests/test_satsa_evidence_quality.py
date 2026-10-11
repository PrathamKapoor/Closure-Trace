"""Unit tests for EvidenceQualityWorker and ingest-time scope validation."""
import time
from satsa.analysis.workers.evidence_quality import (
    DEFAULT_EVIDENCE_QUALITY_POLICY,
    EvidenceQualityThresholds,
    EvidenceQualityWorker,
)
from satsa.contracts.worker import RunContext, SnapshotRef
from satsa.domain.evidence import Finding
from satsa.domain.workflow import Alert, Case, Disposition, InvestigationStep
from satsa.store.dataset import CanonicalDataset


def test_evidence_quality_out_of_period():
    now = time.time()
    p_start = now
    p_end = now + 1000

    # 1 alert within period, 1 alert before, 1 alert after
    a_ok = Alert(entity_id="e1", assessment_id="a1", native_id="A1", created_at=now + 500, source_record_ref="src_1")
    a_early = Alert(entity_id="e1", assessment_id="a1", native_id="A2", created_at=now - 200, source_record_ref="src_2")
    a_late = Alert(entity_id="e1", assessment_id="a1", native_id="A3", created_at=now + 1500, source_record_ref="src_3")

    ds = CanonicalDataset(
        entity_id="e1",
        assessment_id="a1",
        period_start=p_start,
        period_end=p_end,
        alerts=[a_ok, a_early, a_late],
        cases=[],
    )

    worker = EvidenceQualityWorker()
    ctx = RunContext("r1", "e1", "a1", "1.0", now)
    batch = worker.evaluate(SnapshotRef("", "e1", "a1"), ds, [], None, ctx)

    assert batch.state == "signal"
    findings = [f for f in batch.findings if f.rule_or_category == "evidence_quality.out_of_period"]
    assert len(findings) == 1
    f = findings[0]
    assert a_early.id in f.scoped_subjects
    assert a_late.id in f.scoped_subjects
    assert "src_2" in f.evidence_refs
    assert "src_3" in f.evidence_refs


def test_evidence_quality_chronology_violation():
    now = time.time()
    # Alert closed before created
    a_bad = Alert(
        entity_id="e1",
        assessment_id="a1",
        native_id="A1",
        created_at=now + 200,
        closed_at=now + 100,
        source_record_ref="src_a",
    )
    # Case closed before opened
    c_bad = Case(
        entity_id="e1",
        assessment_id="a1",
        native_id="C1",
        opened_at=now + 300,
        closed_at=now + 50,
    )
    # Step performed before case opened
    step_bad = InvestigationStep(
        case_id=c_bad.id,
        action_type="inspect",
        performed_at=now + 20,
        sequence=1,
    )

    ds = CanonicalDataset(
        entity_id="e1",
        assessment_id="a1",
        alerts=[a_bad],
        cases=[c_bad],
        steps=[step_bad],
    )

    worker = EvidenceQualityWorker()
    ctx = RunContext("r1", "e1", "a1", "1.0", now)
    batch = worker.evaluate(SnapshotRef("", "e1", "a1"), ds, [], None, ctx)

    assert batch.state == "signal"
    findings = [f for f in batch.findings if f.rule_or_category == "evidence_quality.chronology_violation"]
    assert len(findings) == 1
    f = findings[0]
    assert a_bad.id in f.scoped_subjects
    assert c_bad.id in f.scoped_subjects
    assert step_bad.id in f.scoped_subjects


def test_evidence_quality_contradictory_dispositions():
    now = time.time()
    a1 = Alert(entity_id="e1", assessment_id="a1", native_id="A1", created_at=now, source_record_ref="src_a1")
    # Dispositions for same alert claiming true_positive AND benign
    d1 = Disposition(
        entity_id="e1", assessment_id="a1", occurred_at=now + 10,
        alert_id=a1.id, mapped_category="true_positive",
    )
    d2 = Disposition(
        entity_id="e1", assessment_id="a1", occurred_at=now + 20,
        alert_id=a1.id, mapped_category="benign",
    )

    ds = CanonicalDataset(
        entity_id="e1",
        assessment_id="a1",
        alerts=[a1],
        dispositions=[d1, d2],
    )

    worker = EvidenceQualityWorker()
    ctx = RunContext("r1", "e1", "a1", "1.0", now)
    batch = worker.evaluate(SnapshotRef("", "e1", "a1"), ds, [], None, ctx)

    assert batch.state == "signal"
    findings = [f for f in batch.findings if f.rule_or_category == "evidence_quality.contradictory_dispositions"]
    assert len(findings) == 1
    f = findings[0]
    assert a1.id in f.scoped_subjects


def test_evidence_quality_incompatible_workflow_states():
    now = time.time()
    a1 = Alert(entity_id="e1", assessment_id="a1", native_id="A1", created_at=now, closed_at=None, source_record_ref="src_a1")
    c1 = Case(
        entity_id="e1",
        assessment_id="a1",
        native_id="C1",
        opened_at=now,
        status="closed",
        closed_at=now + 50,
        alert_refs=[a1.id],
    )

    ds = CanonicalDataset(
        entity_id="e1",
        assessment_id="a1",
        alerts=[a1],
        cases=[c1],
    )

    worker = EvidenceQualityWorker()
    ctx = RunContext("r1", "e1", "a1", "1.0", now)
    batch = worker.evaluate(SnapshotRef("", "e1", "a1"), ds, [], None, ctx)

    assert batch.state == "signal"
    findings = [f for f in batch.findings if f.rule_or_category == "evidence_quality.incompatible_workflow_states"]
    assert len(findings) == 1
    f = findings[0]
    assert c1.id in f.scoped_subjects
    assert a1.id in f.scoped_subjects
