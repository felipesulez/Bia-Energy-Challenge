from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Assignment:
    record_id: int
    usuario_id: int
    usuario_nombre: str

    metodo: str

    score_zona: float
    score_carga: float
    score_total: float

    carga_antes: int
    carga_despues: int

    capacidad_antes: float
    capacidad_despues: float

    utilizacion_antes: float

    coincidencia_zona: bool
    fallback_geografico: bool
    estado_geografico: str
    explicacion_zona: str

    razon: str