from datetime import date

from fastapi.testclient import TestClient

from assignment_engine.persistence.assignment_repository import (
    AssignmentRepository,
)
from assignment_engine.persistence.database import Database
from assignment_engine.persistence.record_repository import RecordRepository

from app.dependencies import (
    build_assignment_service,
    get_reassign_context,
    load_assignment_data,
)
from app.main import app


def test_reassign_assignment_creates_new_active_assignment(
    tmp_path,
):
    database = Database(tmp_path / "assignments.db")
    database.initialize()

    connection = database.connect()

    try:
        repository = AssignmentRepository(connection)
        record_repository = RecordRepository(connection)

        users, records, absences = load_assignment_data()

        record_repository.initialize_records(
            [
                {
                    "id": record.id,
                    "estado": record.estado,
                }
                for record in records
            ]
        )

        service = build_assignment_service(
            repository=repository,
            record_repository=record_repository,
        )

        service.execute_pending_records(
            records=records,
            users=users,
            absences=absences,
            evaluation_date=date(2026, 10, 3),
            executed_by="felipe",
        )

        assignments = service.list_assignments()

        original_assignment = next(
            assignment
            for assignment in assignments
            if assignment["es_activa"] is True
        )

        original_assignment_id = original_assignment["assignment_id"]
        original_record_id = original_assignment["record_id"]
        original_user_id = original_assignment["usuario_id"]

        app.dependency_overrides[get_reassign_context] = (
            lambda: (
                service,
                users,
                records,
                absences,
            )
        )

        client = TestClient(app)

        response = client.post(
            f"/assignments/{original_assignment_id}/reassign",
            json={
                "evaluation_date": "2026-10-03",
                "executed_by": "felipe",
            },
        )

        assert response.status_code == 200

        reassignment = response.json()

        assert reassignment["record_id"] == original_record_id
        assert reassignment["usuario_id"] != original_user_id
        assert (
            reassignment["reemplaza_assignment_id"]
            == original_assignment_id
        )
        assert reassignment["es_activa"] is True

        history = service.list_assignments()

        old_assignment = next(
            assignment
            for assignment in history
            if assignment["assignment_id"] == original_assignment_id
        )

        new_assignment = next(
            assignment
            for assignment in history
            if (
                assignment["assignment_id"]
                == reassignment["assignment_id"]
            )
        )

        assert old_assignment["es_activa"] is False
        assert new_assignment["es_activa"] is True

    finally:
        app.dependency_overrides.pop(
            get_reassign_context,
            None,
        )
        connection.close()