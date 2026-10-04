from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from assignment_engine.utils.normalization import normalize_text


@dataclass(frozen=True)
class Record:
    id: int
    razon_social: str
    nit: str
    sector: Optional[str]
    empleados: Optional[int]
    ingresos_estimados: Optional[float]
    ciudad: str
    zona: Optional[str]
    fuente: str
    notas: Optional[str]
    estado: str
    fecha_creacion: datetime

    @property
    def zona_normalizada(self) -> Optional[str]:
        """
        Return the normalized record zone for comparisons.
        """

        return normalize_text(self.zona)