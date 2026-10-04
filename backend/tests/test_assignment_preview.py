from fastapi.testclient import TestClient

from assignment_engine.persistence.assignment_repository import (
    AssignmentRepository,
)
from assignment_engine.persistence.database import Database

from app.dependencies import (
    build_assignment_service,
    get_preview_context,
    load_assignment_data,
)
from app.main import app

def test_preview_does_not_persist_assignments(tmp_path):
    database = Database(tmp_path / "preview.db")
    database.initialize()

    connection = database.connect()
    repository = AssignmentRepository(connection)

    service = build_assignment_service(repository=repository)
    users, records, absences = load_assignment_data()

    app.dependency_overrides[get_preview_context] = (
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
            "/assignments/preview",
            json={
                "evaluation_date": "2026-10-03",
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

        assert assignments_count == 0
        assert traces_count == 0
        assert active_assignments_count == 0

    finally:
        app.dependency_overrides.clear()
        connection.close()


def test_preview_pending_assignments_returns_assignments_and_traces():
    client = TestClient(app)

    response = client.post(
        "/assignments/preview",
        json={
            "evaluation_date": "2026-10-03",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert "assignments" in body
    assert "traces" in body
    assert isinstance(body["assignments"], list)
    assert isinstance(body["traces"], list)

def test_preview_returns_real_assignments():
    client = TestClient(app)

    response = client.post(
        "/assignments/preview",
        json={
            "evaluation_date": "2026-10-03",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert len(body["assignments"]) == 71
    assert len(body["traces"]) == 71

def test_preview_response_schema_accepts_typed_assignment():
    client = TestClient(app)

    response = client.post(
        "/assignments/preview",
        json={
            "evaluation_date": "2026-10-03",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert len(body["assignments"]) == 71
    assert len(body["traces"]) == 71

    assert body["assignments"][0]["record_id"] > 0
    assert body["assignments"][0]["usuario_id"] > 0

    assert body["traces"][0]["record_id"] > 0
    assert body["traces"][0]["usuario_seleccionado_id"] > 0

def test_preview_rejects_invalid_evaluation_date():
    client = TestClient(app)

    response = client.post(
        "/assignments/preview",
        json={
            "evaluation_date": "not-a-date",
        },
    )

    assert response.status_code == 422

    client = TestClient(app)

    response = client.post(
        "/assignments/preview",
        json={
            "evaluation_date": "2026-10-03",
        },
    )

    assert response.status_code == 200

    from app.dependencies import get_preview_context

    service, users, records, absences = get_preview_context()

    assert service.repository is None