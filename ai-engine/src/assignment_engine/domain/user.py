from dataclasses import dataclass
from datetime import date
from typing import Optional

from assignment_engine.utils.normalization import normalize_text


@dataclass
class User:
    id: int
    nombre: str
    email: str
    rol: str
    equipo_id: Optional[int]
    zona: Optional[str]
    segmento_experto: Optional[str]
    capacidad_maxima: Optional[int]
    fecha_ingreso: Optional[date]
    activo: bool

    carga_actual: int = 0
    capacidad_disponible: Optional[int] = None

    def __post_init__(self) -> None:
        if self.capacidad_maxima is not None:
            self.capacidad_disponible = (
                self.capacidad_maxima - self.carga_actual
            )

    @property
    def zona_normalizada(self) -> Optional[str]:
        """
        Return the normalized user zone for comparisons.
        """

        return normalize_text(self.zona)