from fastapi.testclient import TestClient

from assignment_engine.persistence.assignment_repository import (
    AssignmentRepository,
)
from assignment_engine.persistence.database import Database
from assignment_engine.persistence.record_repository import RecordRepository

from app.dependencies import (
    build_assignment_service,
    get_execute_context,
    load_assignment_data,
)
from app.main import app


def test_get_assignments_returns_assignment_history(tmp_path):
    database = Database(tmp_path / "assignments.db")
    database.initialize()

    connection = database.connect()
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
        evaluation_date=__import__("datetime").date(2026, 10, 3),
        executed_by="felipe",
    )

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

        response = client.get("/assignments")

        assert response.status_code == 200

        body = response.json()

        assert "assignments" in body
        assert "total" in body

        assert body["total"] == 71
        assert len(body["assignments"]) == 71

        assignment = body["assignments"][0]

        assert assignment["assignment_id"] > 0
        assert assignment["record_id"] > 0
        assert assignment["usuario_id"] > 0

        assert assignment["ejecutado_por"] == "felipe"
        assert assignment["ejecutado_en"] is not None
        assert assignment["es_activa"] is True

    finally:
        app.dependency_overrides.clear()
        connection.close()