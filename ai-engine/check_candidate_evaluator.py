from datetime import datetime
from assignment_engine.domain.record import Record
from assignment_engine.domain.user import User
from assignment_engine.rules.candidate_evaluator import (
    CandidateEvaluator,
)


record = Record(
    id=1,
    razon_social="Empresa de prueba",
    nit="900123456-1",
    sector="servicios",
    empleados=50,
    ingresos_estimados=1_000_000_000,
    ciudad="Bogotá",
    zona="Centro",
    fuente="web",
    notas=None,
    estado="nuevo",
    fecha_creacion=datetime(2026, 10, 1),
)


user = User(
    id=10,
    nombre="Jorge Iván Arango",
    email="jorge@example.com",
    rol="vendedor",
    equipo_id=2,
    zona="centro",
    segmento_experto="industrial",
    capacidad_maxima=40,
    fecha_ingreso=datetime(2024, 1, 1).date(),
    activo=True,
)

user.carga_actual = 10
user.capacidad_disponible = (
    user.capacidad_maxima - user.carga_actual
)


evaluator = CandidateEvaluator()

candidate = evaluator.evaluate(
    record,
    user,
)


print("=== EVALUACIÓN DE CANDIDATO ===")

print("Usuario:", candidate.usuario_id)
print("Nombre:", candidate.nombre)
print("Score zona:", candidate.score_zona)
print("Score carga:", round(candidate.score_carga, 2))
print("Score total:", round(candidate.score_total, 2))
print("Carga actual:", candidate.carga_actual)
print(
    "Capacidad disponible:",
    candidate.capacidad_disponible,
)
print(
    "Utilización:",
    round(candidate.utilizacion, 4),
)