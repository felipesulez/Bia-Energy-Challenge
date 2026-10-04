from datetime import date
from typing import Iterable

from assignment_engine.domain.absence import Absence
from assignment_engine.domain.user import User


class EligibilityRule:
    """
    Determines whether a user is eligible to receive assignments.
    """

    ASSIGNABLE_ROLES = {"vendedor", "lider"}

    def is_eligible(
        self,
        user: User,
        active_absence_user_ids: set[int],
    ) -> bool:
        """
        Return True when the user satisfies all hard eligibility constraints.
        """

        if not user.activo:
            return False

        if user.rol.strip().lower() not in self.ASSIGNABLE_ROLES:
            return False

        if user.id in active_absence_user_ids:
            return False

        if user.capacidad_maxima is None:
            return False

        if user.capacidad_maxima <= 0:
            return False

        if user.capacidad_disponible is None:
            return False

        if user.capacidad_disponible <= 0:
            return False

        return True

    def filter_eligible(
        self,
        users: Iterable[User],
        active_absence_user_ids: set[int],
    ) -> list[User]:
        """
        Return only users that satisfy the eligibility rules.
        """

        return [
            user
            for user in users
            if self.is_eligible(
                user,
                active_absence_user_ids,
            )
        ]


def get_active_absence_user_ids(
    absences: Iterable[Absence],
    evaluation_date: date,
) -> set[int]:
    """
    Return user IDs with an active absence on the evaluation date.
    """

    return {
        absence.usuario_id
        for absence in absences
        if absence.is_active_on(evaluation_date)
    }