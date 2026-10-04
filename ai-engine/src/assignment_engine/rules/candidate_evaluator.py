from assignment_engine.domain.candidate import Candidate
from assignment_engine.domain.record import Record
from assignment_engine.domain.user import User
from assignment_engine.rules.geographic import calculate_zone_score
from assignment_engine.rules.scoring import calculate_load_score


class CandidateEvaluator:
    """
    Evaluates a user as a candidate for a record.

    This class combines the individual scoring rules:
    - geographic score
    - load-balance score
    """

    def evaluate(
        self,
        record: Record,
        user: User,
    ) -> Candidate:
        """
        Calculate all scores for a record-user pair.
        """

        score_zona = calculate_zone_score(
            record.zona_normalizada,
            user.zona_normalizada,
        )

        score_carga = calculate_load_score(
            user.carga_actual,
            user.capacidad_maxima,
        )

        score_total = score_zona + score_carga

        utilizacion = (
            user.carga_actual
            / user.capacidad_maxima
        )

        return Candidate(
            usuario_id=user.id,
            nombre=user.nombre,
            score_zona=score_zona,
            score_carga=score_carga,
            score_total=score_total,
            carga_actual=user.carga_actual,
            capacidad_disponible=user.capacidad_disponible,
            utilizacion=utilizacion,
        )