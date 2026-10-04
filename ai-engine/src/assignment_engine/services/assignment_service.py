import copy
from datetime import date

from assignment_engine.domain.absence import Absence
from assignment_engine.domain.assignment_batch_result import AssignmentBatchResult
from assignment_engine.domain.record import Record
from assignment_engine.domain.user import User
from assignment_engine.engine.weighted_rules import WeightedRulesEngine
from assignment_engine.persistence.assignment_repository import AssignmentRepository
from assignment_engine.rules.eligibility import get_active_absence_user_ids


class AssignmentService:
    PENDING_STATUS = "nuevo"

    def __init__(
        self,
        engine: WeightedRulesEngine,
        repository: AssignmentRepository | None = None,
    ) -> None:
        self.engine = engine
        self.repository = repository

    def preview_pending_records(
        self,
        records: list[Record],
        users: list[User],
        absences: list[Absence],
        evaluation_date: date,
    ) -> AssignmentBatchResult:
        """Preview pending assignments without modifying original users."""

        preview_users = copy.deepcopy(users)

        return self._assign_pending_records(
            records=records,
            users=preview_users,
            absences=absences,
            evaluation_date=evaluation_date,
        )

    def execute_pending_records(
        self,
        records: list[Record],
        users: list[User],
        absences: list[Absence],
        evaluation_date: date,
        executed_by: str,
    ) -> AssignmentBatchResult:
        """Execute and persist pending assignments."""

        if self.repository is None:
            raise ValueError(
                "AssignmentRepository is required for execution."
            )

        result = self._assign_pending_records(
            records=records,
            users=users,
            absences=absences,
            evaluation_date=evaluation_date,
        )

        self.repository.save_many(
            results=[
                type_result
                for type_result in (
                    self._to_assignment_results(result)
                )
            ],
            executed_by=executed_by,
        )

        return result

    def assign_pending_records(
        self,
        records: list[Record],
        users: list[User],
        absences: list[Absence],
        evaluation_date: date,
    ) -> AssignmentBatchResult:
        """Execute assignments using the provided user state."""

        return self._assign_pending_records(
            records=records,
            users=users,
            absences=absences,
            evaluation_date=evaluation_date,
        )

    def _assign_pending_records(
        self,
        records: list[Record],
        users: list[User],
        absences: list[Absence],
        evaluation_date: date,
    ) -> AssignmentBatchResult:
        active_absence_user_ids = get_active_absence_user_ids(
            absences,
            evaluation_date,
        )

        pending_records = self._get_pending_records(records)

        assignments = []
        traces = []

        for record in pending_records:
            result = self.engine.assign(
                record=record,
                users=users,
                active_absence_user_ids=active_absence_user_ids,
            )

            if result is not None:
                assignments.append(result.assignment)
                traces.append(result.trace)

        return AssignmentBatchResult(
            assignments=tuple(assignments),
            traces=tuple(traces),
        )

    @staticmethod
    def _to_assignment_results(
        batch_result: AssignmentBatchResult,
    ):
        from assignment_engine.domain.assignment_result import AssignmentResult

        return [
            AssignmentResult(
                assignment=assignment,
                trace=trace,
            )
            for assignment, trace in zip(
                batch_result.assignments,
                batch_result.traces,
            )
        ]

    def _get_pending_records(
        self,
        records: list[Record],
    ) -> list[Record]:
        return [
            record
            for record in records
            if record.estado.strip().lower() == self.PENDING_STATUS
        ]