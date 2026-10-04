from assignment_engine.domain.assignment_trace import (
    AssignmentTrace,
)
from assignment_engine.domain.candidate import Candidate


candidates = (
    Candidate(
        usuario_id=10,
        nombre="Usuario A",
        score_zona=60.0,
        score_carga=30.0,
        score_total=90.0,
        carga_actual=10,
        capacidad_disponible=30,
        utilizacion=0.25,
    ),
    Candidate(
        usuario_id=30,
        nombre="Usuario C",
        score_zona=60.0,
        score_carga=20.0,
        score_total=80.0,
        carga_actual=20,
        capacidad_disponible=20,
        utilizacion=0.50,
    ),
    Candidate(
        usuario_id=20,
        nombre="Usuario B",
        score_zona=0.0,
        score_carga=35.0,
        score_total=35.0,
        carga_actual=5,
        capacidad_disponible=35,
        utilizacion=0.125,
    ),
)


trace = AssignmentTrace(
    record_id=1,
    metodo="weighted_rules",
    candidatos=candidates,
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


print("=== PRUEBA ASSIGNMENT TRACE ===")

print("Registro:", trace.record_id)
print("Método:", trace.metodo)
print(
    "Candidatos evaluados:",
    len(trace.candidatos),
)
print(
    "Usuario seleccionado:",
    trace.usuario_seleccionado_id,
)
print(
    "Estado geográfico:",
    trace.estado_geografico,
)
print(
    "Razón:",
    trace.razon,
)

print("\n=== RANKING ===")

for position, candidate in enumerate(
    trace.candidatos,
    start=1,
):
    print(
        f"#{position} "
        f"Usuario {candidate.usuario_id} "
        f"| Score total: {candidate.score_total:.2f}"
    )