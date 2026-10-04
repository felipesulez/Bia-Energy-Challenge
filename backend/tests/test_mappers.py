from datetime import date
from pathlib import Path

from assignment_engine.data.loader import (
    load_absences,
    load_records,
    load_users,
)
from assignment_engine.engine.weighted_rules import WeightedRulesEngine
from assignment_engine.rules.candidate_evaluator import CandidateEvaluator
from assignment_engine.rules.eligibility import EligibilityRule
from assignment_engine.services.assignment_service import AssignmentService

from app.mappers import to_preview_response


DATA_DIR = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "raw"
    / "data-opcion-a"
    / "data-opcion-a"
)


def test_preview_mapper_returns_typed_response():
    users = load_users(DATA_DIR / "usuarios.csv")
    records = load_records(DATA_DIR / "registros.csv")
    absences = load_absences(DATA_DIR / "ausencias.csv")

    engine = WeightedRulesEngine(
        eligibility_rule=EligibilityRule(),
        candidate_evaluator=CandidateEvaluator(),
    )

    service = AssignmentService(engine)

    result = service.preview_pending_records(
        records=records,
        users=users,
        absences=absences,
        evaluation_date=date(2026, 10, 3),
    )

    response = to_preview_response(result)

    assert len(response.assignments) == 71
    assert len(response.traces) == 71

    assert response.assignments[0].record_id > 0
    assert response.assignments[0].usuario_id > 0

    assert response.traces[0].record_id > 0
    assert response.traces[0].usuario_seleccionado_id > 0