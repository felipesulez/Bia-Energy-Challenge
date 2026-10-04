import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

from assignment_engine.domain.assignment_result import AssignmentResult


class AssignmentRepository:
    """Persist assignments and their audit traces."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    @contextmanager
    def transaction(self):
        """Provide an explicit transaction boundary for a use case."""

        try:
            self.connection.execute("BEGIN")

            yield

            self.connection.commit()

        except Exception:
            self.connection.rollback()
            raise

    def save(
        self,
        result: AssignmentResult,
        executed_by: str = "system",
        executed_at: str | None = None,
        replaces_assignment_id: int | None = None,
    ) -> int:
        """Save one assignment and its trace in one transaction."""

        with self.connection:
            if replaces_assignment_id is not None:
                self.connection.execute(
                    """
                    DELETE FROM active_assignments
                    WHERE assignment_id = ?
                    """,
                    (replaces_assignment_id,),
                )

            return self._save_one(
                result=result,
                executed_by=executed_by,
                executed_at=executed_at,
                replaces_assignment_id=replaces_assignment_id,
            )

    def save_many(
        self,
        results: list[AssignmentResult] | tuple[AssignmentResult, ...],
        executed_by: str = "system",
        executed_at: str | None = None,
    ) -> list[int]:
        """Save a batch of assignments and traces."""

        assignment_ids = []

        with self.connection:
            for result in results:
                assignment_id = self._save_one(
                    result=result,
                    executed_by=executed_by,
                    executed_at=executed_at,
                    replaces_assignment_id=None,
                )

                assignment_ids.append(assignment_id)

        return assignment_ids

    def save_many_without_transaction(
        self,
        results: list[AssignmentResult] | tuple[AssignmentResult, ...],
        executed_by: str = "system",
        executed_at: str | None = None,
    ) -> list[int]:
        """
        Save a batch without opening or committing a transaction.

        The caller owns the transaction boundary.
        """

        assignment_ids = []

        for result in results:
            assignment_id = self._save_one(
                result=result,
                executed_by=executed_by,
                executed_at=executed_at,
                replaces_assignment_id=None,
            )

            assignment_ids.append(assignment_id)

        return assignment_ids

    def get_active_record_ids(self) -> set[int]:
        """Return record IDs that currently have an active assignment."""

        rows = self.connection.execute(
            """
            SELECT record_id
            FROM active_assignments
            """
        ).fetchall()

        return {row["record_id"] for row in rows}

    def get_active_assignment(self, record_id: int):
        """Return the active assignment for a record, if any."""

        return self.connection.execute(
            """
            SELECT
                record_id,
                assignment_id,
                usuario_id,
                assigned_at
            FROM active_assignments
            WHERE record_id = ?
            """,
            (record_id,),
        ).fetchone()

    def list_assignments(self) -> list[dict]:
        """Return assignment history with traceability information."""

        rows = self.connection.execute(
            """
            SELECT
                a.id AS assignment_id,
                a.record_id,
                a.usuario_id,
                a.metodo,
                a.score_zona,
                a.score_carga,
                a.score_total,
                a.carga_antes,
                a.carga_despues,
                a.capacidad_antes,
                a.capacidad_despues,
                a.utilizacion_antes,
                a.coincidencia_zona,
                a.fallback_geografico,
                a.estado_geografico,
                a.explicacion_zona,
                a.razon,
                t.ejecutado_por,
                t.ejecutado_en,
                t.reemplaza_assignment_id,
                CASE
                    WHEN aa.assignment_id IS NOT NULL
                    THEN 1
                    ELSE 0
                END AS es_activa
            FROM assignments a
            INNER JOIN assignment_traces t
                ON t.assignment_id = a.id
            LEFT JOIN active_assignments aa
                ON aa.assignment_id = a.id
            ORDER BY a.id ASC
            """
        ).fetchall()

        return [
            {
                "assignment_id": row["assignment_id"],
                "record_id": row["record_id"],
                "usuario_id": row["usuario_id"],
                "metodo": row["metodo"],
                "score_zona": row["score_zona"],
                "score_carga": row["score_carga"],
                "score_total": row["score_total"],
                "carga_antes": row["carga_antes"],
                "carga_despues": row["carga_despues"],
                "capacidad_antes": row["capacidad_antes"],
                "capacidad_despues": row["capacidad_despues"],
                "utilizacion_antes": row["utilizacion_antes"],
                "coincidencia_zona": bool(row["coincidencia_zona"]),
                "fallback_geografico": bool(row["fallback_geografico"]),
                "estado_geografico": row["estado_geografico"],
                "explicacion_zona": row["explicacion_zona"],
                "razon": row["razon"],
                "ejecutado_por": row["ejecutado_por"],
                "ejecutado_en": row["ejecutado_en"],
                "reemplaza_assignment_id": row[
                    "reemplaza_assignment_id"
                ],
                "es_activa": bool(row["es_activa"]),
            }
            for row in rows
        ]


    def _save_one(
        self,
        result: AssignmentResult,
        executed_by: str,
        executed_at: str | None,
        replaces_assignment_id: int | None,
    ) -> int:
        """Persist one assignment and its trace."""

        assignment = result.assignment
        trace = result.trace

        timestamp = executed_at or datetime.now(
            timezone.utc
        ).isoformat()

        candidates_json = json.dumps(
            [
                {
                    "usuario_id": candidate.usuario_id,
                    "nombre": candidate.nombre,
                    "score_zona": candidate.score_zona,
                    "score_carga": candidate.score_carga,
                    "score_total": candidate.score_total,
                    "carga_actual": candidate.carga_actual,
                    "capacidad_disponible": candidate.capacidad_disponible,
                    "utilizacion": candidate.utilizacion,
                }
                for candidate in trace.candidatos
            ],
            ensure_ascii=False,
        )

        cursor = self.connection.execute(
            """
            INSERT INTO assignments (
                record_id, usuario_id, metodo,
                score_zona, score_carga, score_total,
                carga_antes, carga_despues,
                capacidad_antes, capacidad_despues,
                utilizacion_antes,
                coincidencia_zona, fallback_geografico,
                estado_geografico, explicacion_zona, razon,
                ejecutado_en
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                assignment.record_id,
                assignment.usuario_id,
                assignment.metodo,
                assignment.score_zona,
                assignment.score_carga,
                assignment.score_total,
                assignment.carga_antes,
                assignment.carga_despues,
                assignment.capacidad_antes,
                assignment.capacidad_despues,
                assignment.utilizacion_antes,
                int(assignment.coincidencia_zona),
                int(assignment.fallback_geografico),
                assignment.estado_geografico,
                assignment.explicacion_zona,
                assignment.razon,
                timestamp,
            ),
        )

        assignment_id = cursor.lastrowid

        self.connection.execute(
            """
            INSERT INTO assignment_traces (
                assignment_id, record_id, metodo, parametros,
                usuario_seleccionado_id,
                criterio_seleccion, criterio_desempate,
                candidatos_json, estado_geografico,
                coincidencia_zona, fallback_geografico,
                explicacion_zona, razon,
                ejecutado_por, ejecutado_en,
                reemplaza_assignment_id,
                prompt, respuesta_modelo
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                assignment_id,
                trace.record_id,
                trace.metodo,
                json.dumps(
                    trace.parametros,
                    ensure_ascii=False,
                ),
                trace.usuario_seleccionado_id,
                trace.criterio_seleccion,
                trace.criterio_desempate,
                candidates_json,
                trace.estado_geografico,
                int(trace.coincidencia_zona),
                int(trace.fallback_geografico),
                trace.explicacion_zona,
                trace.razon,
                executed_by,
                timestamp,
                replaces_assignment_id,
                trace.prompt,
                trace.respuesta_modelo,
            ),
        )

        self.connection.execute(
            """
            INSERT INTO active_assignments (
                record_id,
                assignment_id,
                usuario_id,
                assigned_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                assignment.record_id,
                assignment_id,
                assignment.usuario_id,
                timestamp,
            ),
        )

        return assignment_id