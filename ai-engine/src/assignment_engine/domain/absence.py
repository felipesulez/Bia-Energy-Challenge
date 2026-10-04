from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class Absence:
    id: int
    usuario_id: int
    desde: date
    hasta: Optional[date]
    motivo: Optional[str]

    def is_active_on(self, evaluation_date: date) -> bool:
        """
        Return True when the absence is active on the given date.
        """

        return (
            self.desde <= evaluation_date
            and (
                self.hasta is None
                or self.hasta >= evaluation_date
            )
        )