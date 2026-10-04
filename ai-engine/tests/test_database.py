
import sqlite3

from assignment_engine.persistence.database import Database


def test_database_creates_connection(tmp_path):
    database_path = tmp_path / "test.db"

    database = Database(database_path)
    connection = database.connect()

    try:
        assert isinstance(connection, sqlite3.Connection)
        assert connection.execute(
            "PRAGMA foreign_keys"
        ).fetchone()[0] == 1
    finally:
        connection.close()


def test_database_initializes_schema(tmp_path):
    database = Database(
        tmp_path / "nested" / "test.db"
    )

    database.initialize()

    with database.connect() as connection:
        tables = {
            row["name"]
            for row in connection.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                """
            )
        }

    assert "assignments" in tables
    assert "assignment_traces" in tables