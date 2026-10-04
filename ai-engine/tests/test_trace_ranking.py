from datetime import date

from assignment_engine.domain.record import Record
from assignment_engine.domain.user import User
from assignment_engine.engine.weighted_rules import WeightedRulesEngine
from assignment_engine.rules.candidate_evaluator import CandidateEvaluator
from assignment_engine.rules.eligibility import EligibilityRule


def test_trace_preserves_complete_deterministic_ranking():
    """The trace must preserve the complete candidate ranking."""

    engine = WeightedRulesEngine(
        eligibility_rule=EligibilityRule(),
        candidate_evaluator=CandidateEvaluator(),
    )

    record = Record(
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

    users = [
        User(
            id=1,
            nombre="Usuario 1",
            email="usuario1@test.com",
            rol="vendedor",
            equipo_id=1,
            zona="centro",
            segmento_experto="pyme",
            capacidad_maxima=40,
            fecha_ingreso=date(2026, 1, 1),
            activo=True,
            carga_actual=10,
        ),
        User(
            id=2,
            nombre="Usuario 2",
            email="usuario2@test.com",
            rol="vendedor",
            equipo_id=1,
            zona="centro",
            segmento_experto="pyme",
            capacidad_maxima=40,
            fecha_ingreso=date(2026, 1, 1),
            activo=True,
            carga_actual=20,
        ),
        User(
            id=3,
            nombre="Usuario 3",
            email="usuario3@test.com",
            rol="vendedor",
            equipo_id=1,
            zona="centro",
            segmento_experto="pyme",
            capacidad_maxima=40,
            fecha_ingreso=date(2026, 1, 1),
            activo=True,
            carga_actual=30,
        ),
    ]

    result = engine.assign(
        record=record,
        users=users,
        active_absence_user_ids=set(),
    )

    assert result is not None

    trace = result.trace

    # The trace must contain every eligible candidate.
    assert len(trace.candidatos) == 3

    # The first candidate must be the selected user.
    assert (
        trace.candidatos[0].usuario_id
        == trace.usuario_seleccionado_id
    )

    assert (
        trace.candidatos[0].usuario_id
        == result.assignment.usuario_id
    )

    # The complete ranking must be ordered by total score.
    assert (
        trace.candidatos[0].score_total
        >= trace.candidatos[1].score_total
    )

    assert (
        trace.candidatos[1].score_total
        >= trace.candidatos[2].score_total
    )

    # The ranking must preserve the three candidate IDs.
    assert [
        candidate.usuario_id
        for candidate in trace.candidatos
    ] == [1, 2, 3]