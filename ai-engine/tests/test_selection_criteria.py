from datetime import date

from assignment_engine.domain.record import Record
from assignment_engine.domain.user import User
from assignment_engine.rules.candidate_evaluator import CandidateEvaluator
from assignment_engine.rules.eligibility import EligibilityRule
from assignment_engine.engine.weighted_rules import WeightedRulesEngine


def build_engine() -> WeightedRulesEngine:
    """Build a Weighted Rules engine with its dependencies."""

    return WeightedRulesEngine(
        eligibility_rule=EligibilityRule(),
        candidate_evaluator=CandidateEvaluator(),
    )


def build_record() -> Record:
    """Build a minimal record for controlled selection tests."""

    return Record(
        id=1,
        razon_social="Empresa de prueba",
        nit="900000001",
        sector="comercio",
        empleados=10,
        ingresos_estimados=1000000.0,
        ciudad="Popayán",
        zona="centro",
        fuente="test",
        notas=None,
        estado="nuevo",
        fecha_creacion=date(2026, 10, 3),
    )


def build_user(
    user_id: int,
    capacity: int,
    current_load: int = 0,
) -> User:
    """Build an eligible user for controlled selection tests."""

    return User(
        id=user_id,
        nombre=f"Usuario {user_id}",
        email=f"usuario{user_id}@test.com",
        rol="vendedor",
        equipo_id=1,
        zona="centro",
        segmento_experto="pyme",
        capacidad_maxima=capacity,
        fecha_ingreso=date(2026, 1, 1),
        activo=True,
        carga_actual=current_load,
    )


def test_selects_candidate_with_highest_total_score():
    """
    The candidate with the highest total score must be selected.
    No tie-break should be registered.
    """

    engine = build_engine()
    record = build_record()

    users = [
        build_user(user_id=1, capacity=40, current_load=10),
        build_user(user_id=2, capacity=40, current_load=30),
    ]

    result = engine.assign(
        record=record,
        users=users,
        active_absence_user_ids=set(),
    )

    assert result is not None

    assert result.assignment.usuario_id == 1
    assert result.trace.usuario_seleccionado_id == 1

    assert result.trace.criterio_seleccion == "mayor_score_total"
    assert result.trace.criterio_desempate is None

    assert len(result.trace.candidatos) == 2

    assert result.trace.candidatos[0].usuario_id == 1
    assert result.trace.candidatos[1].usuario_id == 2

    assert (
        result.trace.candidatos[0].score_total
        > result.trace.candidatos[1].score_total
    )


def test_resolves_score_tie_with_highest_available_capacity():
    """
    When total scores are tied, the candidate with the highest
    available capacity must be selected.
    """

    engine = build_engine()
    record = build_record()

    users = [
        build_user(user_id=1, capacity=40, current_load=10),
        build_user(user_id=2, capacity=80, current_load=20),
    ]

    result = engine.assign(
        record=record,
        users=users,
        active_absence_user_ids=set(),
    )

    assert result is not None

    assert result.assignment.usuario_id == 2
    assert result.trace.usuario_seleccionado_id == 2

    assert result.trace.criterio_seleccion == "mayor_score_total"
    assert (
        result.trace.criterio_desempate
        == "mayor_capacidad_disponible"
    )

    assert len(result.trace.candidatos) == 2

    assert result.trace.candidatos[0].usuario_id == 2
    assert result.trace.candidatos[1].usuario_id == 1

    assert (
        result.trace.candidatos[0].score_total
        == result.trace.candidatos[1].score_total
    )

    assert (
        result.trace.candidatos[0].capacidad_disponible
        > result.trace.candidatos[1].capacidad_disponible
    )

def test_resolves_score_and_capacity_tie_with_lowest_user_id():
    """
    When total score and available capacity are tied, the candidate
    with the lowest user ID must be selected.
    """

    engine = build_engine()
    record = build_record()

    users = [
        build_user(user_id=1, capacity=40, current_load=10),
        build_user(user_id=2, capacity=40, current_load=10),
    ]

    result = engine.assign(
        record=record,
        users=users,
        active_absence_user_ids=set(),
    )

    assert result is not None

    assert result.assignment.usuario_id == 1
    assert result.trace.usuario_seleccionado_id == 1

    assert result.trace.criterio_seleccion == "mayor_score_total"
    assert (
        result.trace.criterio_desempate
        == "menor_usuario_id"
    )

    assert len(result.trace.candidatos) == 2

    assert result.trace.candidatos[0].usuario_id == 1
    assert result.trace.candidatos[1].usuario_id == 2

    assert (
        result.trace.candidatos[0].score_total
        == result.trace.candidatos[1].score_total
    )

    assert (
        result.trace.candidatos[0].capacidad_disponible
        == result.trace.candidatos[1].capacidad_disponible
    )