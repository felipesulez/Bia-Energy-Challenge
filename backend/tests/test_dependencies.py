from app.dependencies import (
    build_assignment_service,
    load_assignment_data,
)


def test_build_assignment_service():
    service = build_assignment_service()

    assert service is not None


def test_load_assignment_data():
    users, records, absences = load_assignment_data()

    assert len(users) == 18
    assert len(records) == 167
    assert len(absences) == 8