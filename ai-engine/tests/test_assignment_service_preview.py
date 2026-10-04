from copy import deepcopy
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


DATA_DIR = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "raw"
    / "data-opcion-a"
    / "data-opcion-a"
)

EVALUATION_DATE = date(2026, 10, 3)


def build_service() -> AssignmentService:
    eligibility_rule = EligibilityRule()
    candidate_evaluator = CandidateEvaluator()

    engine = WeightedRulesEngine(
        eligibility_rule=eligibility_rule,
        candidate_evaluator=candidate_evaluator,
    )

    return AssignmentService(engine)


def test_preview_matches_real_assignment_engine():
    users = load_users(DATA_DIR / "usuarios.csv")
    records = load_records(DATA_DIR / "registros.csv")
    absences = load_absences(DATA_DIR / "ausencias.csv")

    original_users = deepcopy(users)

    service = build_service()

    result = service.preview_pending_records(
        records=records,
        users=users,
        absences=absences,
        evaluation_date=EVALUATION_DATE,
    )

    assert len(result.assignments) == 71
    assert len(result.traces) == 71

    assert sum(
        assignment.carga_despues - assignment.carga_antes
        for assignment in result.assignments
    ) == 71

    assert sum(
        assignment.capacidad_antes - assignment.capacidad_despues
        for assignment in result.assignments
    ) == 71

    assert sum(
        assignment.coincidencia_zona
        for assignment in result.assignments
    ) == 55

    assert sum(
        assignment.fallback_geografico
        for assignment in result.assignments
    ) == 11

    assert sum(
        assignment.estado_geografico == "zona_no_informada"
        for assignment in result.assignments
    ) == 5

    assert all(
        not assignment.fallback_geografico
        or assignment.estado_geografico
        == "fallback_sin_candidato_en_zona"
        for assignment in result.assignments
    )

    assert all(
        assignment.score_total
        == assignment.score_zona + assignment.score_carga
        for assignment in result.assignments
    )

    assert users == original_users


def test_preview_preserves_original_user_capacity():
    users = load_users(DATA_DIR / "usuarios.csv")
    records = load_records(DATA_DIR / "registros.csv")
    absences = load_absences(DATA_DIR / "ausencias.csv")

    original_capacity = {
        user.id: (
            user.carga_actual,
            user.capacidad_disponible,
        )
        for user in users
    }

    service = build_service()

    service.preview_pending_records(
        records=records,
        users=users,
        absences=absences,
        evaluation_date=EVALUATION_DATE,
    )

    current_capacity = {
        user.id: (
            user.carga_actual,
            user.capacidad_disponible,
        )
        for user in users
    }

    assert current_capacity == original_capacity