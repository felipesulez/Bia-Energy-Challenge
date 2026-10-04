
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