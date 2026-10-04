from pathlib import Path

from assignment_engine.persistence.database import Database


def test_schema_creates_audit_tables(tmp_path):
    database_path = tmp_path / "test.db"
    database = Database(database_path)

    schema_path = (
        Path(__file__).parents[1]
        / "src"
        / "assignment_engine"
        / "persistence"
        / "schema.sql"
    )

    with database.connect() as connection:
        schema = schema_path.read_text(encoding="utf-8")
        connection.executescript(schema)

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

        columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(assignment_traces)"
            )
        }

        assert "candidatos_json" in columns
        assert "parametros" in columns
        assert "prompt" in columns
        assert "respuesta_modelo" in columns