from assignment_engine.domain.assignment import Assignment
from assignment_engine.domain.assignment_result import (
    AssignmentResult,
)
from assignment_engine.domain.assignment_trace import (
    AssignmentTrace,
)
from assignment_engine.domain.candidate import Candidate


candidate = Candidate(
    usuario_id=10,
    nombre="Usuario A",
    score_zona=60.0,
    score_carga=30.0,
    score_total=90.0,
    carga_actual=10,
    capacidad_disponible=30,
    utilizacion=0.25,
)


assignment = Assignment(
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


trace = AssignmentTrace(
    record_id=1,
    metodo="weighted_rules",
    candidatos=(candidate,),
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


result = AssignmentResult(
    assignment=assignment,
    trace=trace,
)


print("=== PRUEBA ASSIGNMENT RESULT ===")

print(
    "Registro:",
    result.assignment.record_id,
)

print(
    "Usuario asignado:",
    result.assignment.usuario_id,
)

print(
    "Método:",
    result.assignment.metodo,
)

print(
    "Score total:",
    result.assignment.score_total,
)

print(
    "Usuario seleccionado en trace:",
    result.trace.usuario_seleccionado_id,
)

print(
    "Candidatos en trace:",
    len(result.trace.candidatos),
)

print(
    "Estado geográfico:",
    result.trace.estado_geografico,
)

print("\n=== VALIDACIONES ===")

assert result.assignment.record_id == result.trace.record_id

assert (
    result.assignment.usuario_id
    == result.trace.usuario_seleccionado_id
)

assert (
    result.assignment.metodo
    == result.trace.metodo
)

assert (
    result.assignment.estado_geografico
    == result.trace.estado_geografico
)

assert len(result.trace.candidatos) == 1

print("✓ Assignment y Trace corresponden al mismo registro")
print("✓ Assignment y Trace corresponden al mismo usuario")
print("✓ Assignment y Trace utilizan el mismo método")
print("✓ Estado geográfico consistente")
print("✓ Candidatos almacenados correctamente")

print("\n=== PRUEBA COMPLETADA ===")