from fastapi.testclient import TestClient

from assignment_engine.persistence.assignment_repository import (
    AssignmentRepository,
)
from assignment_engine.persistence.database import Database

from app.dependencies import (
    build_assignment_service,
    get_execute_context,
    load_assignment_data,
)
from app.main import app


def test_execute_persists_assignments(tmp_path):
    database = Database(tmp_path / "execute.db")
    database.initialize()

    connection = database.connect()
    repository = AssignmentRepository(connection)

    service = build_assignment_service(repository=repository)
    users, records, absences = load_assignment_data()

    app.dependency_overrides[get_execute_context] = (
        lambda: (
            service,
            users,
            records,
            absences,
        )
    )

    try:
        client = TestClient(app)

        response = client.post(
            "/assignments/execute",
            json={
                "evaluation_date": "2026-10-03",
                "executed_by": "felipe",
            },
        )

        assert response.status_code == 200

        body = response.json()

        assert len(body["assignments"]) == 71
        assert len(body["traces"]) == 71

        assignments_count = connection.execute(
            "SELECT COUNT(*) FROM assignments"
        ).fetchone()[0]

        traces_count = connection.execute(
            "SELECT COUNT(*) FROM assignment_traces"
        ).fetchone()[0]

        active_assignments_count = connection.execute(
            "SELECT COUNT(*) FROM active_assignments"
        ).fetchone()[0]

        assert assignments_count == 71
        assert traces_count == 71
        assert active_assignments_count == 71

    finally:
        app.dependency_overrides.clear()
        connection.close()


def test_execute_is_idempotent_for_active_records(tmp_path):
    database = Database(tmp_path / "execute.db")
    database.initialize()

    connection = database.connect()
    repository = AssignmentRepository(connection)

    service = build_assignment_service(repository=repository)
    users, records, absences = load_assignment_data()

    app.dependency_overrides[get_execute_context] = (
        lambda: (
            service,
            users,
            records,
            absences,
        )
    )

    try:
        client = TestClient(app)

        first_response = client.post(
            "/assignments/execute",
            json={
                "evaluation_date": "2026-10-03",
                "executed_by": "felipe",
            },
        )

        assert first_response.status_code == 200

        first_body = first_response.json()

        assert len(first_body["assignments"]) == 71
        assert len(first_body["traces"]) == 71

        second_response = client.post(
            "/assignments/execute",
            json={
                "evaluation_date": "2026-10-03",
                "executed_by": "felipe",
            },
        )

        assert second_response.status_code == 200

        second_body = second_response.json()

        assert len(second_body["assignments"]) == 0
        assert len(second_body["traces"]) == 0

        assignments_count = connection.execute(
            "SELECT COUNT(*) FROM assignments"
        ).fetchone()[0]

        traces_count = connection.execute(
            "SELECT COUNT(*) FROM assignment_traces"
        ).fetchone()[0]

        active_assignments_count = connection.execute(
            "SELECT COUNT(*) FROM active_assignments"
        ).fetchone()[0]

        assert assignments_count == 71
        assert traces_count == 71
        assert active_assignments_count == 71

    finally:
        app.dependency_overrides.clear()
        connection.close()