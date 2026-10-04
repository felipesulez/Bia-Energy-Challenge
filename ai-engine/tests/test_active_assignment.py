from datetime import date
from pathlib import Path

import pytest

from assignment_engine.data.loader import (
    load_absences,
    load_records,
    load_users,
)
from assignment_engine.engine.weighted_rules import WeightedRulesEngine
from assignment_engine.persistence.assignment_repository import AssignmentRepository
from assignment_engine.persistence.database import Database
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


def build_service(repository):
    eligibility_rule = EligibilityRule()
    candidate_evaluator = CandidateEvaluator()

    engine = WeightedRulesEngine(
        eligibility_rule=eligibility_rule,
        candidate_evaluator=candidate_evaluator,
    )

    return AssignmentService(
        engine=engine,
        repository=repository,
    )


def load_test_data():
    users = load_users(DATA_DIR / "usuarios.csv")
    records = load_records(DATA_DIR / "registros.csv")
    absences = load_absences(DATA_DIR / "ausencias.csv")

    return users, records, absences


def test_saved_assignment_becomes_active(tmp_path):
    database = Database(tmp_path / "test.db")
    database.initialize()

    users, records, absences = load_test_data()

    with database.connect() as connection:
        repository = AssignmentRepository(connection)
        service = build_service(repository)

        result = service.execute_pending_records(
            records=records,
            users=users,
            absences=absences,
            evaluation_date=EVALUATION_DATE,
            executed_by="felipe.sulez",
        )

        active_assignments = connection.execute(
            """
            SELECT record_id, assignment_id, usuario_id
            FROM active_assignments
            ORDER BY record_id
            """
        ).fetchall()

    assert len(result.assignments) == 71
    assert len(active_assignments) == 71

    assert all(
        row["assignment_id"] is not None
        and row["usuario_id"] is not None
        for row in active_assignments
    )


def test_record_cannot_have_two_active_assignments(tmp_path):
    database = Database(tmp_path / "test.db")
    database.initialize()

    users, records, absences = load_test_data()

    with database.connect() as connection:
        repository = AssignmentRepository(connection)
        service = build_service(repository)

        result = service.execute_pending_records(
            records=records,
            users=users,
            absences=absences,
            evaluation_date=EVALUATION_DATE,
            executed_by="felipe.sulez",
        )

        assignment = result.assignments[0]

        with pytest.raises(Exception):
            connection.execute(
                """
                INSERT INTO active_assignments (
                    record_id,
                    assignment_id,
                    usuario_id,
                    assigned_at
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    assignment.record_id,
                    999999,
                    assignment.usuario_id,
                    "2026-10-03T12:00:00+00:00",
                ),
            )


def test_execute_does_not_duplicate_existing_assignment(tmp_path):
    database = Database(tmp_path / "test.db")
    database.initialize()

    users, records, absences = load_test_data()

    with database.connect() as connection:
        repository = AssignmentRepository(connection)
        service = build_service(repository)

        first_result = service.execute_pending_records(
            records=records,
            users=users,
            absences=absences,
            evaluation_date=EVALUATION_DATE,
            executed_by="felipe.sulez",
        )

        first_assignment_count = connection.execute(
            "SELECT COUNT(*) FROM assignments"
        ).fetchone()[0]

        first_active_count = connection.execute(
            "SELECT COUNT(*) FROM active_assignments"
        ).fetchone()[0]

        second_result = service.execute_pending_records(
            records=records,
            users=users,
            absences=absences,
            evaluation_date=EVALUATION_DATE,
            executed_by="felipe.sulez",
        )

        second_assignment_count = connection.execute(
            "SELECT COUNT(*) FROM assignments"
        ).fetchone()[0]

        second_active_count = connection.execute(
            "SELECT COUNT(*) FROM active_assignments"
        ).fetchone()[0]

    assert len(first_result.assignments) == 71
    assert first_assignment_count == 71
    assert first_active_count == 71

    assert len(second_result.assignments) == 0
    assert second_assignment_count == 71
    assert second_active_count == 71


def test_reassignment_replaces_active_assignment(tmp_path):
    database = Database(tmp_path / "test.db")
    database.initialize()

    users, records, absences = load_test_data()

    record = records[0]

    with database.connect() as connection:
        repository = AssignmentRepository(connection)
        service = build_service(repository)

        first_result = service.assign_record(
            record=record,
            users=users,
            absences=absences,
            evaluation_date=EVALUATION_DATE,
            executed_by="felipe.sulez",
        )

        first_assignment_id = connection.execute(
            """
            SELECT id
            FROM assignments
            WHERE record_id = ?
            """,
            (record.id,),
        ).fetchone()[0]

        first_user_id = first_result.assignment.usuario_id

        second_result = service.reassign_record(
            record=record,
            users=users,
            absences=absences,
            evaluation_date=EVALUATION_DATE,
            executed_by="felipe.sulez",
        )

        active_assignment = connection.execute(
            """
            SELECT assignment_id, usuario_id
            FROM active_assignments
            WHERE record_id = ?
            """,
            (record.id,),
        ).fetchone()

        trace = connection.execute(
            """
            SELECT reemplaza_assignment_id
            FROM assignment_traces
            WHERE assignment_id = ?
            """,
            (active_assignment["assignment_id"],),
        ).fetchone()

        assignment_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM assignments
            WHERE record_id = ?
            """,
            (record.id,),
        ).fetchone()[0]

    assert first_result.assignment.usuario_id == first_user_id

    assert second_result.assignment.usuario_id != first_user_id

    assert assignment_count == 2

    assert active_assignment["assignment_id"] != first_assignment_id
    assert active_assignment["usuario_id"] == second_result.assignment.usuario_id

    assert trace["reemplaza_assignment_id"] == first_assignment_id