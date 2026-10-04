import sqlite3
from datetime import date
from pathlib import Path

import pytest

from assignment_engine.data.loader import (
    load_absences,
    load_records,
    load_users,
)
from assignment_engine.engine.weighted_rules import WeightedRulesEngine
from assignment_engine.persistence.database import Database
from assignment_engine.persistence.assignment_repository import (
    AssignmentRepository,
)
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


def build_assignment_results():
    users = load_users(DATA_DIR / "usuarios.csv")
    records = load_records(DATA_DIR / "registros.csv")
    absences = load_absences(DATA_DIR / "ausencias.csv")

    service = build_service()

    results = []

    active_absence_user_ids = {
        absence.usuario_id
        for absence in absences
        if absence.is_active_on(EVALUATION_DATE)
    }

    for record in records:
        if record.estado.strip().lower() != "nuevo":
            continue

        result = service.engine.assign(
            record=record,
            users=users,
            active_absence_user_ids=active_absence_user_ids,
        )

        if result is not None:
            results.append(result)

    return results


def test_repository_saves_assignment_batch(tmp_path):
    database = Database(tmp_path / "test.db")
    database.initialize()

    results = build_assignment_results()

    assert len(results) == 71

    with database.connect() as connection:
        repository = AssignmentRepository(connection)

        assignment_ids = repository.save_many(
            results=results,
            executed_by="test-user",
        )

        assert len(assignment_ids) == 71

        assignments_count = connection.execute(
            "SELECT COUNT(*) FROM assignments"
        ).fetchone()[0]

        traces_count = connection.execute(
            "SELECT COUNT(*) FROM assignment_traces"
        ).fetchone()[0]

    assert assignments_count == 71
    assert traces_count == 71


def test_repository_links_each_trace_to_its_assignment(tmp_path):
    database = Database(tmp_path / "test.db")
    database.initialize()

    results = build_assignment_results()

    with database.connect() as connection:
        repository = AssignmentRepository(connection)

        repository.save_many(
            results=results,
            executed_by="test-user",
        )

        rows = connection.execute(
            """
            SELECT
                a.id AS assignment_id,
                t.assignment_id AS trace_assignment_id,
                a.record_id,
                t.record_id AS trace_record_id
            FROM assignments a
            JOIN assignment_traces t
                ON t.assignment_id = a.id
            ORDER BY a.id
            """
        ).fetchall()

    assert len(rows) == 71

    for row in rows:
        assert row["assignment_id"] == row["trace_assignment_id"]
        assert row["record_id"] == row["trace_record_id"]


def test_repository_rolls_back_entire_batch_on_failure(tmp_path):
    database = Database(tmp_path / "test.db")
    database.initialize()

    results = build_assignment_results()

    assert len(results) == 71

    with database.connect() as connection:
        repository = AssignmentRepository(connection)

        original_save = repository._save_one

        calls = 0

        def failing_save_one(*args, **kwargs):
            nonlocal calls

            calls += 1

            if calls == 10:
                raise sqlite3.IntegrityError(
                    "simulated batch failure"
                )

            return original_save(*args, **kwargs)

        repository._save_one = failing_save_one

        with pytest.raises(sqlite3.IntegrityError):
            repository.save_many(
                results=results,
                executed_by="test-user",
            )

        assignments_count = connection.execute(
            "SELECT COUNT(*) FROM assignments"
        ).fetchone()[0]

        traces_count = connection.execute(
            "SELECT COUNT(*) FROM assignment_traces"
        ).fetchone()[0]

    assert assignments_count == 0
    assert traces_count == 0