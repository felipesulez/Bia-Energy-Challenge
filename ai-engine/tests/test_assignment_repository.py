
import json
from datetime import date
from pathlib import Path

import pytest

from assignment_engine.domain.record import Record
from assignment_engine.domain.user import User
from assignment_engine.engine.weighted_rules import WeightedRulesEngine
from assignment_engine.persistence.assignment_repository import (
    AssignmentRepository,
)
from assignment_engine.persistence.database import Database
from assignment_engine.rules.candidate_evaluator import CandidateEvaluator
from assignment_engine.rules.eligibility import EligibilityRule


SCHEMA_PATH = (
    Path(__file__).parents[1]
    / "src"
    / "assignment_engine"
    / "persistence"
    / "schema.sql"
)


def build_assignment_result():
    engine = WeightedRulesEngine(
        eligibility_rule=EligibilityRule(),
        candidate_evaluator=CandidateEvaluator(),
    )

    record = Record(
        id=101,
        razon_social="Empresa de prueba",
        nit="900000101",
        sector="comercio",
        empleados=10,
        ingresos_estimados=1_000_000.0,
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
            nombre="Vendedor de prueba",
            email="vendedor@test.com",
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
            nombre="Segundo vendedor",
            email="vendedor2@test.com",
            rol="vendedor",
            equipo_id=1,
            zona="centro",
            segmento_experto="pyme",
            capacidad_maxima=40,
            fecha_ingreso=date(2026, 1, 1),
            activo=True,
            carga_actual=20,
        ),
    ]

    result = engine.assign(
        record=record,
        users=users,
        active_absence_user_ids=set(),
    )

    assert result is not None
    return result


@pytest.fixture
def database(tmp_path):
    database = Database(tmp_path / "test.db")

    with database.connect() as connection:
        connection.executescript(
            SCHEMA_PATH.read_text(encoding="utf-8")
        )

    yield database


def test_repository_saves_assignment_and_trace(database):
    result = build_assignment_result()

    with database.connect() as connection:
        repository = AssignmentRepository(connection)

        assignment_id = repository.save(
            result,
            executed_by="felipe",
            executed_at="2026-10-04T10:00:00+00:00",
        )

        assignment = connection.execute(
            "SELECT * FROM assignments WHERE id = ?",
            (assignment_id,),
        ).fetchone()

        trace = connection.execute(
            """
            SELECT *
            FROM assignment_traces
            WHERE assignment_id = ?
            """,
            (assignment_id,),
        ).fetchone()

        assert assignment is not None
        assert trace is not None

        assert assignment["record_id"] == result.assignment.record_id
        assert assignment["usuario_id"] == result.assignment.usuario_id

        assert trace["usuario_seleccionado_id"] == (
            result.trace.usuario_seleccionado_id
        )
        assert trace["ejecutado_por"] == "felipe"

        candidates = json.loads(trace["candidatos_json"])
        parameters = json.loads(trace["parametros"])

        assert len(candidates) == len(result.trace.candidatos)
        assert candidates[0]["usuario_id"] == (
            result.trace.usuario_seleccionado_id
        )
        assert parameters == result.trace.parametros

        assert trace["prompt"] is None
        assert trace["respuesta_modelo"] is None



def test_repository_saves_active_assignment(database):
    result = build_assignment_result()

    with database.connect() as connection:
        repository = AssignmentRepository(connection)

        assignment_id = repository.save(
            result,
            executed_by="felipe",
            executed_at="2026-10-04T10:00:00+00:00",
        )

        active_assignment = connection.execute(
            """
            SELECT record_id, assignment_id, usuario_id, assigned_at
            FROM active_assignments
            WHERE record_id = ?
            """,
            (result.assignment.record_id,),
        ).fetchone()

    assert active_assignment is not None

    assert active_assignment["record_id"] == (
        result.assignment.record_id
    )

    assert active_assignment["assignment_id"] == assignment_id

    assert active_assignment["usuario_id"] == (
        result.assignment.usuario_id
    )

    assert active_assignment["assigned_at"] == (
        "2026-10-04T10:00:00+00:00"
    )

def test_repository_rolls_back_assignment_if_trace_fails(database):
    result = build_assignment_result()

    with database.connect() as connection:
        repository = AssignmentRepository(connection)

        # This referenced assignment does not exist.
        # The foreign-key violation occurs while inserting the trace.
        with pytest.raises(Exception):
            repository.save(
                result,
                replaces_assignment_id=999999,
            )

        assignment_count = connection.execute(
            "SELECT COUNT(*) FROM assignments"
        ).fetchone()[0]

        trace_count = connection.execute(
            "SELECT COUNT(*) FROM assignment_traces"
        ).fetchone()[0]

        assert assignment_count == 0
        assert trace_count == 0


def test_repository_lists_assignment_history(database):
    result = build_assignment_result()

    with database.connect() as connection:
        repository = AssignmentRepository(connection)

        assignment_id = repository.save(
            result,
            executed_by="felipe",
            executed_at="2026-10-04T10:00:00+00:00",
        )

        history = repository.list_assignments()

    assert len(history) == 1

    assignment = history[0]

    assert assignment["assignment_id"] == assignment_id
    assert assignment["record_id"] == result.assignment.record_id
    assert assignment["usuario_id"] == result.assignment.usuario_id
    assert assignment["metodo"] == result.assignment.metodo
    assert assignment["score_total"] == result.assignment.score_total
    assert assignment["ejecutado_por"] == "felipe"
    assert assignment["ejecutado_en"] == (
        "2026-10-04T10:00:00+00:00"
    )
    assert assignment["es_activa"] is True
    assert assignment["reemplaza_assignment_id"] is None


def test_repository_lists_reassignment_history(database):
    first_result = build_assignment_result()

    with database.connect() as connection:
        repository = AssignmentRepository(connection)

        first_assignment_id = repository.save(
            first_result,
            executed_by="felipe",
            executed_at="2026-10-04T10:00:00+00:00",
        )

        second_result = build_assignment_result()

        second_assignment_id = repository.save(
            second_result,
            executed_by="paula",
            executed_at="2026-10-04T11:00:00+00:00",
            replaces_assignment_id=first_assignment_id,
        )

        history = repository.list_assignments()

    assert len(history) == 2

    assignments_by_id = {
        assignment["assignment_id"]: assignment
        for assignment in history
    }

    first_assignment = assignments_by_id[first_assignment_id]
    second_assignment = assignments_by_id[second_assignment_id]

    assert first_assignment["es_activa"] is False
    assert second_assignment["es_activa"] is True

    assert first_assignment["reemplaza_assignment_id"] is None
    assert second_assignment["reemplaza_assignment_id"] == (
        first_assignment_id
    )

    assert first_assignment["ejecutado_por"] == "felipe"
    assert second_assignment["ejecutado_por"] == "paula"


def test_repository_lists_assignments_with_traceability_fields(database):
    result = build_assignment_result()

    with database.connect() as connection:
        repository = AssignmentRepository(connection)

        repository.save(
            result,
            executed_by="felipe",
            executed_at="2026-10-04T10:00:00+00:00",
        )

        history = repository.list_assignments()

    assignment = history[0]

    assert assignment["score_zona"] == result.assignment.score_zona
    assert assignment["score_carga"] == result.assignment.score_carga
    assert assignment["carga_antes"] == result.assignment.carga_antes
    assert assignment["carga_despues"] == result.assignment.carga_despues
    assert assignment["capacidad_antes"] == (
        result.assignment.capacidad_antes
    )
    assert assignment["capacidad_despues"] == (
        result.assignment.capacidad_despues
    )
    assert assignment["coincidencia_zona"] == (
        result.assignment.coincidencia_zona
    )
    assert assignment["fallback_geografico"] == (
        result.assignment.fallback_geografico
    )
    assert assignment["estado_geografico"] == (
        result.assignment.estado_geografico
    )
    assert assignment["explicacion_zona"] == (
        result.assignment.explicacion_zona
    )
    assert assignment["razon"] == result.assignment.razon