from datetime import date
from pathlib import Path

from assignment_engine.data.loader import (
    load_absences,
    load_records,
    load_users,
)
from assignment_engine.engine.weighted_rules import WeightedRulesEngine
from assignment_engine.persistence.assignment_repository import (
    AssignmentRepository,
)
from assignment_engine.persistence.database import Database
from assignment_engine.persistence.record_repository import RecordRepository
from assignment_engine.rules.candidate_evaluator import CandidateEvaluator
from assignment_engine.rules.eligibility import (
    EligibilityRule,
    get_active_absence_user_ids,
)
from assignment_engine.services.assignment_service import AssignmentService


DATA_DIR = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "raw"
    / "data-opcion-a"
    / "data-opcion-a"
)

EVALUATION_DATE = date(2026, 10, 3)


def build_service(repository, record_repository):
    eligibility_rule = EligibilityRule()
    candidate_evaluator = CandidateEvaluator()

    engine = WeightedRulesEngine(
        eligibility_rule=eligibility_rule,
        candidate_evaluator=candidate_evaluator,
    )

    return AssignmentService(
        engine=engine,
        repository=repository,
        record_repository=record_repository,
    )


def initialize_record_repository(
    record_repository,
    records,
):
    record_repository.initialize_records(
        [
            {
                "id": record.id,
                "estado": record.estado,
            }
            for record in records
        ]
    )


def test_execute_persists_executed_by_in_trace(tmp_path):
    database = Database(tmp_path / "test.db")
    database.initialize()

    users = load_users(DATA_DIR / "usuarios.csv")
    records = load_records(DATA_DIR / "registros.csv")
    absences = load_absences(DATA_DIR / "ausencias.csv")

    with database.connect() as connection:
        repository = AssignmentRepository(connection)
        record_repository = RecordRepository(connection)

        initialize_record_repository(
            record_repository,
            records,
        )

        service = build_service(
            repository,
            record_repository,
        )

        service.execute_pending_records(
            records=records,
            users=users,
            absences=absences,
            evaluation_date=EVALUATION_DATE,
            executed_by="felipe.sulez",
        )

        rows = connection.execute(
            """
            SELECT ejecutado_por
            FROM assignment_traces
            """
        ).fetchall()

    assert len(rows) == 71

    assert all(
        row["ejecutado_por"] == "felipe.sulez"
        for row in rows
    )


def test_execute_completes_full_assignment_cycle(tmp_path):
    database = Database(tmp_path / "test.db")
    database.initialize()

    users = load_users(DATA_DIR / "usuarios.csv")
    records = load_records(DATA_DIR / "registros.csv")
    absences = load_absences(DATA_DIR / "ausencias.csv")

    active_absence_user_ids = get_active_absence_user_ids(
        absences,
        EVALUATION_DATE,
    )

    eligibility_rule = EligibilityRule()

    eligible_users = eligibility_rule.filter_eligible(
        users,
        active_absence_user_ids,
    )

    eligible_user_ids = {
        user.id
        for user in eligible_users
    }

    initial_capacity = sum(
        user.capacidad_maxima
        for user in eligible_users
    )

    with database.connect() as connection:
        repository = AssignmentRepository(connection)
        record_repository = RecordRepository(connection)

        initialize_record_repository(
            record_repository,
            records,
        )

        service = build_service(
            repository,
            record_repository,
        )

        result = service.execute_pending_records(
            records=records,
            users=users,
            absences=absences,
            evaluation_date=EVALUATION_DATE,
            executed_by="felipe.sulez",
        )

        assignment_count = connection.execute(
            "SELECT COUNT(*) FROM assignments"
        ).fetchone()[0]

        trace_count = connection.execute(
            "SELECT COUNT(*) FROM assignment_traces"
        ).fetchone()[0]

        linked_trace_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM assignment_traces t
            JOIN assignments a
                ON t.assignment_id = a.id
            """
        ).fetchone()[0]

        executed_by_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM assignment_traces
            WHERE ejecutado_por = ?
            """,
            ("felipe.sulez",),
        ).fetchone()[0]

    final_capacity = sum(
        user.capacidad_disponible
        for user in users
        if user.id in eligible_user_ids
    )

    consumed_capacity = initial_capacity - final_capacity

    assert len(result.assignments) == 71
    assert len(result.traces) == 71

    assert assignment_count == 71
    assert trace_count == 71
    assert linked_trace_count == 71
    assert executed_by_count == 71

    assert initial_capacity == 520
    assert consumed_capacity == 71
    assert final_capacity == 449

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
        assignment.carga_despues <= assignment.capacidad_antes
        for assignment in result.assignments
    )

def test_service_lists_assignment_history(tmp_path):
    database = Database(tmp_path / "test.db")
    database.initialize()

    users = load_users(DATA_DIR / "usuarios.csv")
    records = load_records(DATA_DIR / "registros.csv")
    absences = load_absences(DATA_DIR / "ausencias.csv")

    with database.connect() as connection:
        repository = AssignmentRepository(connection)
        record_repository = RecordRepository(connection)

        initialize_record_repository(
            record_repository,
            records,
        )

        service = build_service(
            repository,
            record_repository,
        )

        service.execute_pending_records(
            records=records,
            users=users,
            absences=absences,
            evaluation_date=EVALUATION_DATE,
            executed_by="felipe.sulez",
        )

        history = service.list_assignments()

    assert len(history) == 71

    assert all(
        assignment["es_activa"] is True
        for assignment in history
    )

    assert all(
        assignment["ejecutado_por"] == "felipe.sulez"
        for assignment in history
    )