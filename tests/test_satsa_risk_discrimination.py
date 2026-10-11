"""Unit tests verifying Risk Discrimination Policy v2.0.0 and historical v1.0.0 behavior."""
import json
import pytest

from satsa.analysis.risk import (
    DIMENSION_WEIGHTS,
    EntityRiskProfile,
    compute_entity_risk,
)
from satsa.domain.evidence import ConfidenceVector, Finding
from satsa.analysis.repository import FindingStore, ObservationStore, RunStore


@pytest.fixture()
def engine(tmp_path):
    from qsmlops.database.engine import SQLiteDatabaseEngine
    from qsmlops.database.migrations import MigrationRunner

    eng = SQLiteDatabaseEngine(tmp_path / "satsa.db")
    eng.connect()
    MigrationRunner(eng).migrate()
    yield eng
    eng.close()


def _seed_findings(eng, run_id, findings):
    obs_id = "obs_discrim_test"
    from satsa.domain.evidence import Observation
    ObservationStore(eng).insert(
        Observation(
            id=obs_id, run_id=run_id, worker_name="test-worker",
            detector_version="1.0", entity_id="e_test", assessment_id="a_test",
        ),
        created_at=1000.0,
    )
    for idx, f in enumerate(findings):
        f.id = f"find_{idx}"
        f.observation_id = obs_id
        FindingStore(eng).insert(f, created_at=1000.0 + idx)


def test_risk_discrimination_duplicate_evidence_discount(engine):
    run_id = "run_risk_discrim"
    from satsa.domain.runs import AnalysisRun
    RunStore(engine).insert(
        AnalysisRun(
            id=run_id, entity_id="e_test", assessment_id="a_test",
            snapshot_digest="snap_test",
            status="completed", started_at=1000.0,
        ),
        created_at=1000.0,
    )

    # 4 findings in execution_gap all citing the exact same evidence (duplicate signals)
    duplicate_findings = [
        Finding(
            observation_id="",
            rule_or_category="execution_gap.fast_closure",
            state="signal",
            confidence=ConfidenceVector(analytical_support=0.9, evidence_completeness=0.9),
            evidence_refs=["src_same_1", "src_same_2"],
        )
        for _ in range(4)
    ]
    _seed_findings(engine, run_id, duplicate_findings)

    profile_v1 = compute_entity_risk(engine, "e_test", run_id=run_id, policy_version="1.0.0")
    profile_v2 = compute_entity_risk(engine, "e_test", run_id=run_id, policy_version="2.0.0")

    exec_v1 = next(d for d in profile_v1.dimensions if d.name == "execution_gap")
    exec_v2 = next(d for d in profile_v2.dimensions if d.name == "execution_gap")

    # Under v1, 4 identical findings inflate raw score to near saturation
    # Under v2, overlap is dampened so duplicate evidence doesn't cause artificial score inflation
    assert exec_v2.score < exec_v1.score
    assert profile_v2.policy_version == "2.0.0"
    assert profile_v1.policy_version == "1.0.0"
