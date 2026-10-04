from fastapi.testclient import TestClient

from app.main import app


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