from dataclasses import dataclass


@dataclass(frozen=True)
class Candidate:
    usuario_id: int
    nombre: str
    score_zona: float
    score_carga: float
    score_total: float
    carga_actual: int
    capacidad_disponible: float
    utilizacion: float