from dataclasses import dataclass

from assignment_engine.domain.candidate import Candidate


@dataclass(frozen=True)
class AssignmentTrace:
    record_id: int
    metodo: str

    candidatos: tuple[Candidate, ...]

    usuario_seleccionado_id: int

    criterio_seleccion: str
    criterio_desempate: str | None

    estado_geografico: str
    coincidencia_zona: bool
    fallback_geografico: bool
    explicacion_zona: str

    razon: str

    parametros: dict

    ejecutado_por: str | None = None
    ejecutado_en: str | None = None

    reemplaza_assignment_id: int | None = None

    prompt: str | None = None
    respuesta_modelo: str | None = None
