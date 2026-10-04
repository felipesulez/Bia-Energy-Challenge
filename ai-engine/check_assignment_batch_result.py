from assignment_engine.domain.assignment import Assignment
from assignment_engine.domain.assignment_batch_result import (
    AssignmentBatchResult,
)
from assignment_engine.domain.assignment_trace import (
    AssignmentTrace,
)
from assignment_engine.domain.candidate import Candidate


candidate_1 = Candidate(
    usuario_id=10,
    nombre="Usuario A",
    score_zona=60.0,
    score_carga=30.0,
    score_total=90.0,
    carga_actual=10,
    capacidad_disponible=30,
    utilizacion=0.25,
)

candidate_2 = Candidate(
    usuario_id=20,
    nombre="Usuario B",
    score_zona=0.0,
    score_carga=35.0,
    score_total=35.0,
    carga_actual=5,
    capacidad_disponible=35,
    utilizacion=0.125,
)


assignment_1 = Assignment(
    record_id=1,
    usuario_id=10,
    usuario_nombre="Usuario A",
    metodo="weighted_rules",
    score_zona=60.0,
    score_carga=30.0,
    score_total=90.0,
    carga_antes=10,
    carga_despues=11,
    capacidad_antes=30,
    capacidad_despues=29,
    utilizacion_antes=0.25,
    coincidencia_zona=True,
    fallback_geografico=False,
    estado_geografico="coincidencia_exacta",
    explicacion_zona=(
        "El usuario seleccionado tiene coincidencia "
        "exacta de zona."
    ),
    razon=(
        "Usuario seleccionado por mayor puntuación "
        "total (90.00)."
    ),
)


assignment_2 = Assignment(
    record_id=2,
    usuario_id=20,
    usuario_nombre="Usuario B",
    metodo="weighted_rules",
    score_zona=0.0,
    score_carga=35.0,
    score_total=35.0,
    carga_antes=5,
    carga_despues=6,
    capacidad_antes=35,
    capacidad_despues=34,
    utilizacion_antes=0.125,
    coincidencia_zona=False,
    fallback_geografico=True,
    estado_geografico="fallback_sin_candidato_en_zona",
    explicacion_zona=(
        "No había candidatos elegibles con "
        "coincidencia exacta de zona; se aplicó "
        "fallback geográfico."
    ),
    razon=(
        "Usuario seleccionado por mayor puntuación "
        "total (35.00)."
    ),
)


trace_1 = AssignmentTrace(
    record_id=1,
    metodo="weighted_rules",
    candidatos=(candidate_1, candidate_2),
    usuario_seleccionado_id=10,
    estado_geografico="coincidencia_exacta",
    coincidencia_zona=True,
    fallback_geografico=False,
    explicacion_zona=(
        "El usuario seleccionado tiene coincidencia "
        "exacta de zona."
    ),
    razon=(
        "Usuario seleccionado por mayor puntuación "
        "total (90.00)."
    ),
)


trace_2 = AssignmentTrace(
    record_id=2,
    metodo="weighted_rules",
    candidatos=(candidate_2, candidate_1),
    usuario_seleccionado_id=20,
    estado_geografico="fallback_sin_candidato_en_zona",
    coincidencia_zona=False,
    fallback_geografico=True,
    explicacion_zona=(
        "No había candidatos elegibles con "
        "coincidencia exacta de zona; se aplicó "
        "fallback geográfico."
    ),
    razon=(
        "Usuario seleccionado por mayor puntuación "
        "total (35.00)."
    ),
)


result = AssignmentBatchResult(
    assignments=(
        assignment_1,
        assignment_2,
    ),
    traces=(
        trace_1,
        trace_2,
    ),
)


print("=== PRUEBA ASSIGNMENT BATCH RESULT ===")

print(
    "Asignaciones:",
    len(result.assignments),
)

print(
    "Traces:",
    len(result.traces),
)


print("\n=== ASIGNACIONES ===")

for assignment in result.assignments:
    print(
        f"Registro {assignment.record_id} "
        f"→ Usuario {assignment.usuario_id} "
        f"| Score: {assignment.score_total:.2f}"
    )


print("\n=== TRACES ===")

for trace in result.traces:
    print(
        f"Registro {trace.record_id} "
        f"→ Usuario {trace.usuario_seleccionado_id} "
        f"| Candidatos: {len(trace.candidatos)}"
    )


print("\n=== VALIDACIONES ===")

assert len(result.assignments) == 2
assert len(result.traces) == 2

assert (
    result.assignments[0].record_id
    == result.traces[0].record_id
)

assert (
    result.assignments[1].record_id
    == result.traces[1].record_id
)

assert (
    result.assignments[0].usuario_id
    == result.traces[0].usuario_seleccionado_id
)

assert (
    result.assignments[1].usuario_id
    == result.traces[1].usuario_seleccionado_id
)

assert (
    result.assignments[0].metodo
    == result.traces[0].metodo
)

assert (
    result.assignments[1].metodo
    == result.traces[1].metodo
)

print("✓ Las asignaciones fueron almacenadas correctamente")
print("✓ Los traces fueron almacenados correctamente")
print("✓ Cantidad de assignments y traces consistente")
print("✓ Registro 1 consistente entre assignment y trace")
print("✓ Registro 2 consistente entre assignment y trace")
print("✓ Usuarios seleccionados consistentes")
print("✓ Métodos consistentes")

print("\n=== PRUEBA COMPLETADA ===")