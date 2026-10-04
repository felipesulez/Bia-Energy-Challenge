import copy

from assignment_engine.domain.assignment_batch_result import AssignmentBatchResult
from assignment_engine.domain.assignment_result import AssignmentResult
from assignment_engine.engine.weighted_rules import WeightedRulesEngine
from assignment_engine.persistence.assignment_repository import AssignmentRepository
from assignment_engine.rules.eligibility import get_active_absence_user_ids


class AssignmentService:
    PENDING_STATUS = "nuevo"

    def __init__(self, engine, repository=None):
        self.engine = engine
        self.repository = repository

    def preview_pending_records(
        self,
        records,
        users,
        absences,
        evaluation_date,
    ):
        preview_users = copy.deepcopy(users)

        return self._assign_pending_records(
            records=records,
            users=preview_users,
            absences=absences,
            evaluation_date=evaluation_date,
        )

    def execute_pending_records(
        self,
        records,
        users,
        absences,
        evaluation_date,
        executed_by,
    ):
        if self.repository is None:
            raise ValueError(
                "AssignmentRepository is required for execution."
            )

        active_record_ids = self.repository.get_active_record_ids()

        result = self._assign_pending_records(
            records=records,
            users=users,
            absences=absences,
            evaluation_date=evaluation_date,
            excluded_record_ids=active_record_ids,
        )

        self.repository.save_many(
            results=self._to_assignment_results(result),
            executed_by=executed_by,
        )

        return result

    def assign_record(
        self,
        record,
        users,
        absences,
        evaluation_date,
        executed_by,
    ):
        if self.repository is None:
            raise ValueError(
                "AssignmentRepository is required for execution."
            )

        active_assignment = self.repository.get_active_assignment(
            record.id
        )

        if active_assignment is not None:
            raise ValueError(
                f"Record {record.id} already has an active assignment."
            )

        active_absence_user_ids = get_active_absence_user_ids(
            absences,
            evaluation_date,
        )

        result = self.engine.assign(
            record=record,
            users=users,
            active_absence_user_ids=active_absence_user_ids,
        )

        if result is None:
            raise ValueError(
                f"Record {record.id} could not be assigned."
            )

        self.repository.save(
            result=result,
            executed_by=executed_by,
        )

        return result

    def reassign_record(
        self,
        record,
        users,
        absences,
        evaluation_date,
        executed_by,
    ):
        if self.repository is None:
            raise ValueError(
                "AssignmentRepository is required for execution."
            )

        active_assignment = self.repository.get_active_assignment(
            record.id
        )

        if active_assignment is None:
            raise ValueError(
                f"Record {record.id} does not have an active assignment."
            )

        previous_assignment_id = active_assignment["assignment_id"]
        previous_user_id = active_assignment["usuario_id"]

        previous_user = next(
            (
                user
                for user in users
                if user.id == previous_user_id
            ),
            None,
        )

        if previous_user is None:
            raise ValueError(
                f"Previous assigned user {previous_user_id} "
                "was not found."
            )

        # Release the previous user's capacity.
        previous_user.carga_actual -= 1

        if previous_user.carga_actual < 0:
            previous_user.carga_actual = 0

        previous_user.capacidad_disponible = (
            previous_user.capacidad_maxima
            - previous_user.carga_actual
        )

        # Do not allow the same user to receive the record again.
        reassignment_users = [
            user
            for user in users
            if user.id != previous_user_id
        ]

        active_absence_user_ids = get_active_absence_user_ids(
            absences,
            evaluation_date,
        )

        result = self.engine.assign(
            record=record,
            users=reassignment_users,
            active_absence_user_ids=active_absence_user_ids,
        )

        if result is None:
            # Restore the previous user's state if reassignment fails.
            previous_user.carga_actual += 1

            previous_user.capacidad_disponible = (
                previous_user.capacidad_maxima
                - previous_user.carga_actual
            )

            raise ValueError(
                f"Record {record.id} could not be reassigned."
            )

        self.repository.save(
            result=result,
            executed_by=executed_by,
            replaces_assignment_id=previous_assignment_id,
        )

        return result

    def assign_pending_records(
        self,
        records,
        users,
        absences,
        evaluation_date,
    ):
        return self._assign_pending_records(
            records=records,
            users=users,
            absences=absences,
            evaluation_date=evaluation_date,
        )

    def _assign_pending_records(
        self,
        records,
        users,
        absences,
        evaluation_date,
        excluded_record_ids=None,
    ):
        active_absence_user_ids = get_active_absence_user_ids(
            absences,
            evaluation_date,
        )

        excluded_record_ids = excluded_record_ids or set()

        pending_records = self._get_pending_records(
            records,
            excluded_record_ids=excluded_record_ids,
        )

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
    def _to_assignment_results(batch_result):
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
        records,
        excluded_record_ids=None,
    ):
        excluded_record_ids = excluded_record_ids or set()

        return [
            record
            for record in records
            if (
                record.estado.strip().lower() == self.PENDING_STATUS
                and record.id not in excluded_record_ids
            )
        ]