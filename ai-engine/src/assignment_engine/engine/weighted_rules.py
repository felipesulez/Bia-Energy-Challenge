from typing import NamedTuple

from assignment_engine.domain.assignment import Assignment
from assignment_engine.domain.assignment_result import AssignmentResult
from assignment_engine.domain.assignment_trace import AssignmentTrace
from assignment_engine.domain.candidate import Candidate
from assignment_engine.domain.record import Record
from assignment_engine.domain.user import User
from assignment_engine.rules.candidate_evaluator import (
    CandidateEvaluator,
)
from assignment_engine.rules.eligibility import EligibilityRule


class GeographyEvaluation(NamedTuple):
    """Result of evaluating the geographic fit of the selected user."""

    coincidencia_zona: bool
    fallback_geografico: bool
    estado_geografico: str
    explicacion_zona: str


class WeightedRulesEngine:
    """
    Deterministic assignment engine based on weighted rules.

    Selection order:
    1. Highest total score.
    2. Highest available capacity.
    3. Lowest user ID.

    Note: this engine relies on EligibilityRule to exclude users
    without available capacity or with an active absence.
    """

    METHOD_NAME = "weighted_rules"

    METHOD_PARAMETERS = {
        "zone_weight": 60,
        "load_weight": 40,
        "tie_break_order": [
            "score_total",
            "available_capacity",
            "user_id",
        ],
    }

    def __init__(
        self,
        eligibility_rule: EligibilityRule,
        candidate_evaluator: CandidateEvaluator,
    ) -> None:
        self.eligibility_rule = eligibility_rule
        self.candidate_evaluator = candidate_evaluator

    # ------------------------------------------------------------------
    # Ranking
    # ------------------------------------------------------------------
    def _rank(
        self,
        record: Record,
        eligible_users: list[User],
    ) -> list[Candidate]:
        """
        Evaluate and sort already-eligible users.

        Ordering:
        1. Highest total score.
        2. Highest available capacity.
        3. Lowest user ID.
        """

        candidates = [
            self.candidate_evaluator.evaluate(record, user)
            for user in eligible_users
        ]

        candidates.sort(
            key=lambda candidate: (
                -candidate.score_total,
                -candidate.capacidad_disponible,
                candidate.usuario_id,
            )
        )

        return candidates

    def get_ranked_candidates(
        self,
        record: Record,
        users: list[User],
        active_absence_user_ids: set[int],
    ) -> list[Candidate]:
        """
        Return eligible candidates ordered according to the
        deterministic Weighted Rules ranking.
        """

        eligible_users = self.eligibility_rule.filter_eligible(
            users,
            active_absence_user_ids,
        )

        return self._rank(record, eligible_users)

    # ------------------------------------------------------------------
    # Selection criteria
    # ------------------------------------------------------------------

    def _determine_selection_criteria(
        self,
        candidates: list[Candidate],
    ) -> tuple[str, str | None]:
        """
        Determine which ranking criterion produced the selection.

        Returns:
        - selection criterion
        - tie-break criterion, if applicable
        """

        selected = candidates[0]

        same_score = [
            candidate
            for candidate in candidates
            if candidate.score_total == selected.score_total
        ]

        if len(same_score) == 1:
            return "mayor_score_total", None

        same_score_and_capacity = [
            candidate
            for candidate in same_score
            if (
                candidate.capacidad_disponible
                == selected.capacidad_disponible
            )
        ]

        if len(same_score_and_capacity) == 1:
            return (
                "mayor_score_total",
                "mayor_capacidad_disponible",
            )

        return "mayor_score_total", "menor_usuario_id"

    @staticmethod
    def _build_reason(
        selected_candidate: Candidate,
        criterio_desempate: str | None,
        explicacion_zona: str,
    ) -> str:
        """Build the human-readable reason, including the tie-break."""

        razon = (
            "Usuario seleccionado por mayor puntuación "
            f"total ({selected_candidate.score_total:.2f})"
        )

        if criterio_desempate == "mayor_capacidad_disponible":
            razon += ", desempatado por mayor capacidad disponible"

        elif criterio_desempate == "menor_usuario_id":
            razon += ", desempatado por menor ID de usuario"

        return f"{razon}. {explicacion_zona}"

    # ------------------------------------------------------------------
    # Geography
    # ------------------------------------------------------------------

    @staticmethod
    def _evaluate_geography(
        record: Record,
        selected_user: User,
        eligible_users: list[User],
    ) -> GeographyEvaluation:
        """
        Determine the geographic status of the selection.

        Uses the normalized zone of eligible users directly, so it
        does not depend on the internal weights of the evaluator.
        """

        zona_registro = record.zona_normalizada
        zona_usuario = selected_user.zona_normalizada

        # --------------------------------------------------------------
        # No zone informed in the record
        # --------------------------------------------------------------

        if zona_registro is None:
            return GeographyEvaluation(
                coincidencia_zona=False,
                fallback_geografico=False,
                estado_geografico="zona_no_informada",
                explicacion_zona=(
                    "El registro no tiene zona; no se aplicó "
                    "puntuación geográfica."
                ),
            )

        # --------------------------------------------------------------
        # Exact zone match
        # --------------------------------------------------------------

        if (
            zona_usuario is not None
            and zona_registro == zona_usuario
        ):
            return GeographyEvaluation(
                coincidencia_zona=True,
                fallback_geografico=False,
                estado_geografico="coincidencia_exacta",
                explicacion_zona=(
                    "El usuario seleccionado tiene coincidencia "
                    "exacta de zona."
                ),
            )

        # --------------------------------------------------------------
        # Check whether another eligible user belongs to the zone
        # --------------------------------------------------------------

        hay_candidato_en_zona = any(
            user.zona_normalizada == zona_registro
            for user in eligible_users
        )

        # --------------------------------------------------------------
        # No eligible candidate in the record's zone
        # --------------------------------------------------------------

        if not hay_candidato_en_zona:
            return GeographyEvaluation(
                coincidencia_zona=False,
                fallback_geografico=True,
                estado_geografico="fallback_sin_candidato_en_zona",
                explicacion_zona=(
                    "No había candidatos elegibles con "
                    "coincidencia exacta de zona; se aplicó "
                    "fallback geográfico."
                ),
            )

        # --------------------------------------------------------------
        # Candidates existed in the zone, but another user won
        # --------------------------------------------------------------

        return GeographyEvaluation(
            coincidencia_zona=False,
            fallback_geografico=False,
            estado_geografico="seleccion_fuera_de_zona",
            explicacion_zona=(
                "Había candidatos elegibles de la misma "
                "zona, pero otro usuario obtuvo mayor "
                "puntuación total."
            ),
        )

    # ------------------------------------------------------------------
    # Assignment
    # ------------------------------------------------------------------

    def assign(
        self,
        record: Record,
        users: list[User],
        active_absence_user_ids: set[int],
    ) -> AssignmentResult | None:
        """
        Assign a record to the best eligible candidate.

        Returns None when there are no eligible users.

        The user's load and capacity are only mutated after the
        assignment and trace have been built successfully.
        """

        eligible_users = self.eligibility_rule.filter_eligible(
            users,
            active_absence_user_ids,
        )

        candidates = self._rank(
            record,
            eligible_users,
        )

        if not candidates:
            return None

        users_by_id = {
            user.id: user
            for user in eligible_users
        }

        selected_candidate = candidates[0]
        selected_user = users_by_id[
            selected_candidate.usuario_id
        ]

        # --------------------------------------------------------------
        # Determine selection criteria
        # --------------------------------------------------------------

        criterio_seleccion, criterio_desempate = (
            self._determine_selection_criteria(
                candidates
            )
        )

        # --------------------------------------------------------------
        # Evaluate geographic result
        # --------------------------------------------------------------

        geografia = self._evaluate_geography(
            record,
            selected_user,
            eligible_users,
        )

        # --------------------------------------------------------------
        # Build human-readable reason
        # --------------------------------------------------------------

        razon = self._build_reason(
            selected_candidate,
            criterio_desempate,
            geografia.explicacion_zona,
        )

        # --------------------------------------------------------------
        # Calculate state before and after assignment
        # --------------------------------------------------------------

        carga_antes = selected_user.carga_actual
        capacidad_antes = selected_user.capacidad_disponible

        carga_despues = carga_antes + 1
        capacidad_despues = capacidad_antes - 1

        # --------------------------------------------------------------
        # Build assignment
        # --------------------------------------------------------------

        assignment = Assignment(
            record_id=record.id,
            usuario_id=selected_user.id,
            usuario_nombre=selected_user.nombre,
            metodo=self.METHOD_NAME,
            score_zona=selected_candidate.score_zona,
            score_carga=selected_candidate.score_carga,
            score_total=selected_candidate.score_total,
            carga_antes=carga_antes,
            carga_despues=carga_despues,
            capacidad_antes=capacidad_antes,
            capacidad_despues=capacidad_despues,
            utilizacion_antes=selected_candidate.utilizacion,
            coincidencia_zona=geografia.coincidencia_zona,
            fallback_geografico=geografia.fallback_geografico,
            estado_geografico=geografia.estado_geografico,
            explicacion_zona=geografia.explicacion_zona,
            razon=razon,
        )

        # --------------------------------------------------------------
        # Build trace
        # --------------------------------------------------------------

        trace = AssignmentTrace(
            record_id=record.id,
            metodo=self.METHOD_NAME,
            candidatos=tuple(candidates),
            usuario_seleccionado_id=selected_user.id,
            criterio_seleccion=criterio_seleccion,
            criterio_desempate=criterio_desempate,
            estado_geografico=geografia.estado_geografico,
            coincidencia_zona=geografia.coincidencia_zona,
            fallback_geografico=geografia.fallback_geografico,
            explicacion_zona=geografia.explicacion_zona,
            razon=razon,
            parametros=self.METHOD_PARAMETERS,
        )

        # --------------------------------------------------------------
        # Build immutable result
        # --------------------------------------------------------------

        result = AssignmentResult(
            assignment=assignment,
            trace=trace,
        )

        # --------------------------------------------------------------
        # Mutate user state only after everything was built successfully
        # --------------------------------------------------------------

        selected_user.carga_actual = carga_despues
        selected_user.capacidad_disponible = capacidad_despues

        return result