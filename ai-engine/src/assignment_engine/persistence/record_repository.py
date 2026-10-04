from datetime import datetime, timezone

import sqlite3


class RecordRepository:
    """Persist and manage record business status."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def initialize_records(
        self,
        records: list[dict],
    ) -> None:
        """Insert missing records without overwriting existing status."""

        timestamp = datetime.now(timezone.utc).isoformat()

        with self.connection:
            for record in records:
                self.connection.execute(
                    """
                    INSERT OR IGNORE INTO records (
                        id,
                        estado,
                        updated_at
                    )
                    VALUES (?, ?, ?)
                    """,
                    (
                        record["id"],
                        record["estado"],
                        timestamp,
                    ),
                )

    def get_status(self, record_id: int) -> str | None:
        """Return the current business status of a record."""

        row = self.connection.execute(
            """
            SELECT estado
            FROM records
            WHERE id = ?
            """,
            (record_id,),
        ).fetchone()

        if row is None:
            return None

        return row["estado"]

    def update_status(
        self,
        record_id: int,
        status: str,
    ) -> None:
        """Update the business status of an existing record."""

        timestamp = datetime.now(timezone.utc).isoformat()

        cursor = self.connection.execute(
            """
            UPDATE records
            SET estado = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                status,
                timestamp,
                record_id,
            ),
        )

        if cursor.rowcount == 0:
            raise ValueError(
                f"Record {record_id} was not found."
            )