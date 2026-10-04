from datetime import date
from pathlib import Path

from assignment_engine.data.loader import (
    load_absences,
    load_records,
    load_users,
)
from assignment_engine.domain.assignment_batch_result import (
    AssignmentBatchResult,
)
from assignment_engine.engine.weighted_rules import (
    WeightedRulesEngine,
)
from assignment_engine.rules.candidate_evaluator import (
    CandidateEvaluator,
)
from assignment_engine.rules.eligibility import (
    EligibilityRule,
)
from assignment_engine.services.assignment_service import (
    AssignmentService,
)


DATA_DIR = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "raw"
    / "data-opcion-a"
    / "data-opcion-a"
)

EVALUATION_DATE = date(2026, 10, 3)


users = load_users(
    DATA_DIR / "usuarios.csv"
)

absences = load_absences(
    DATA_DIR / "ausencias.csv"
)

records = load_records(
    DATA_DIR / "registros.csv"
)


engine = WeightedRulesEngine(
    eligibility_rule=EligibilityRule(),
    candidate_evaluator=CandidateEvaluator(),
)


service = AssignmentService(
    engine=engine,
)


result = service.assign_pending_records(
    records=records,
    users=users,
    absences=absences,
    evaluation_date=EVALUATION_DATE,
)


print("=== PRUEBA ASSIGNMENT SERVICE ===")

print(
    "Tipo de resultado:",
    type(result).__name__,
)

print(
    "Asignaciones generadas:",
    len(result.assignments),
)

print(
    "Traces generados:",
    len(result.traces),
)


print("\n=== VALIDACIONES ===")

assert isinstance(
    result,
    AssignmentBatchResult,
)

assert len(result.assignments) == 71

assert len(result.traces) == 71

assert len(result.assignments) == len(
    result.traces
)


for assignment, trace in zip(
    result.assignments,
    result.traces,
):
    assert (
        assignment.record_id
        == trace.record_id
    )

    assert (
        assignment.usuario_id
        == trace.usuario_seleccionado_id
    )

    assert (
        assignment.metodo
        == trace.metodo
    )


print("✓ El servicio devuelve AssignmentBatchResult")
print("✓ Se generaron 71 assignments")
print("✓ Se generaron 71 traces")
print("✓ Cada assignment corresponde a su trace")
print("✓ Usuario asignado consistente con el trace")
print("✓ Método consistente entre assignment y trace")

print("\n=== PRUEBA COMPLETADA ===")