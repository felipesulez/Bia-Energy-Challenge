from pathlib import Path

from assignment_engine.persistence.record_repository import (
    RecordRepository,
)

from assignment_engine.persistence.database import Database
from assignment_engine.data.loader import (
    load_absences,
    load_records,
    load_users,
)
from assignment_engine.engine.weighted_rules import WeightedRulesEngine
from assignment_engine.persistence.assignment_repository import (
    AssignmentRepository,
)
from assignment_engine.rules.candidate_evaluator import CandidateEvaluator
from assignment_engine.rules.eligibility import EligibilityRule
from assignment_engine.services.assignment_service import AssignmentService


DATA_DIR = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "raw"
    / "data-opcion-a"
    / "data-opcion-a"
)

DATABASE_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "assignment.db"
)


def get_execute_context():
    database = Database(DATABASE_PATH)
    database.initialize()

    connection = database.connect()

    try:
        repository = AssignmentRepository(connection)
        record_repository = RecordRepository(connection)

        users, records, absences = load_assignment_data()

        record_repository.initialize_records(
            [
                {
                    "id": record.id,
                    "estado": record.estado,
                }
                for record in records
            ]
        )

        service = build_assignment_service(
            repository=repository,
            record_repository=record_repository,
        )

        yield service, users, records, absences
    finally:
        connection.close()

def build_assignment_service(
    repository: AssignmentRepository | None = None,
    record_repository: RecordRepository | None = None,
) -> AssignmentService:
    eligibility_rule = EligibilityRule()
    candidate_evaluator = CandidateEvaluator()

    engine = WeightedRulesEngine(
        eligibility_rule=eligibility_rule,
        candidate_evaluator=candidate_evaluator,
    )

    return AssignmentService(
        engine=engine,
        repository=repository,
        record_repository=record_repository,
    )


def load_assignment_data():
    users = load_users(DATA_DIR / "usuarios.csv")
    records = load_records(DATA_DIR / "registros.csv")
    absences = load_absences(DATA_DIR / "ausencias.csv")

    return users, records, absences


def get_preview_context():
    service = build_assignment_service()
    users, records, absences = load_assignment_data()

    return service, users, records, absences


def get_assignment_history_context():
    database = Database(DATABASE_PATH)
    database.initialize()
    connection = database.connect()

    try:
        repository = AssignmentRepository(connection)
        service = build_assignment_service(repository=repository)
        yield service
    finally:
        connection.close()