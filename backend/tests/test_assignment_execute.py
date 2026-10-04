
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