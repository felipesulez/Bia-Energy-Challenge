from datetime import date

from fastapi.testclient import TestClient

from assignment_engine.persistence.assignment_repository import (
    AssignmentRepository,
)
from assignment_engine.persistence.database import Database
from assignment_engine.persistence.record_repository import RecordRepository

from app.dependencies import get_assignment_history_context
from app.main import app
from app.dependencies import (
    build_assignment_service,
    load_assignment_data,
)


def test_get_assignment_detail_returns_explanation_and_traceability(
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
        assignment_id = assignments[0]["assignment_id"]

        app.dependency_overrides[
            get_assignment_history_context
        ] = lambda: service

        client = TestClient(app)
        response = client.get(
            f"/assignments/{assignment_id}"
        )

        assert response.status_code == 200

        detail = response.json()

        assert detail["assignment_id"] == assignment_id
        assert detail["record_id"] > 0
        assert detail["usuario_id"] > 0
        assert detail["metodo"]
        assert detail["razon"]
        assert detail["explicacion_zona"]

        assert "score_zona" in detail
        assert "score_carga" in detail
        assert "score_total" in detail

        assert "carga_antes" in detail
        assert "carga_despues" in detail
        assert "capacidad_antes" in detail
        assert "capacidad_despues" in detail

        assert detail["ejecutado_por"] == "felipe"
        assert detail["ejecutado_en"] is not None
        assert detail["es_activa"] is True

    finally:
        app.dependency_overrides.pop(
            get_assignment_history_context,
            None,
        )
        connection.close()

def test_get_assignment_detail_returns_404_when_not_found():
    app.dependency_overrides[
        get_assignment_history_context
    ] = lambda: _ServiceWithoutAssignment()

    try:
        client = TestClient(app)
        response = client.get("/assignments/999999")

        assert response.status_code == 404
        assert response.json() == {
            "detail": "Assignment not found."
        }
    finally:
        app.dependency_overrides.pop(
            get_assignment_history_context,
            None,
        )


class _ServiceWithoutAssignment:
    def get_assignment(self, assignment_id: int):
        return None