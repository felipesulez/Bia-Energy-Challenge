from assignment_engine.persistence.database import Database
from assignment_engine.persistence.record_repository import RecordRepository


def test_record_repository_persists_and_updates_record_status(tmp_path):
    database = Database(tmp_path / "records.db")
    database.initialize()

    connection = database.connect()
    repository = RecordRepository(connection)

    try:
        repository.initialize_records(
            [
                {
                    "id": 1,
                    "estado": "nuevo",
                },
                {
                    "id": 2,
                    "estado": "en_gestion",
                },
            ]
        )

        assert repository.get_status(1) == "nuevo"
        assert repository.get_status(2) == "en_gestion"

        repository.update_status(
            record_id=1,
            status="asignado",
        )

        assert repository.get_status(1) == "asignado"
        assert repository.get_status(2) == "en_gestion"

    finally:
        connection.close()

def test_record_repository_initialization_does_not_overwrite_existing_status(
    tmp_path,
):
    database = Database(tmp_path / "records.db")
    database.initialize()

    connection = database.connect()
    repository = RecordRepository(connection)

    try:
        repository.initialize_records(
            [
                {
                    "id": 1,
                    "estado": "nuevo",
                },
            ]
        )

        repository.update_status(
            record_id=1,
            status="asignado",
        )

        repository.initialize_records(
            [
                {
                    "id": 1,
                    "estado": "nuevo",
                },
            ]
        )

        assert repository.get_status(1) == "asignado"

    finally:
        connection.close()