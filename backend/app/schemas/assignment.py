from datetime import date

from pydantic import BaseModel


class AssignmentPreviewRequest(BaseModel):
    evaluation_date: date

class AssignmentExecuteRequest(BaseModel):
    evaluation_date: date
    executed_by: str


    evaluation_date: date
    executed_by: str

class AssignmentResponse(BaseModel):
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


class CandidateResponse(BaseModel):
    usuario_id: int
    nombre: str

    score_zona: float
    score_carga: float
    score_total: float

    carga_actual: int
    capacidad_disponible: float
    utilizacion: float


class AssignmentTraceResponse(BaseModel):
    record_id: int
    metodo: str

    candidatos: list[CandidateResponse]

    usuario_seleccionado_id: int

    criterio_seleccion: str
    criterio_desempate: str | None

    estado_geografico: str
    coincidencia_zona: bool
    fallback_geografico: bool

    explicacion_zona: str
    razon: str

    parametros: dict

    ejecutado_por: str | None
    ejecutado_en: str | None

    reemplaza_assignment_id: int | None

    prompt: str | None
    respuesta_modelo: str | None


class AssignmentPreviewResponse(BaseModel):
    assignments: list[AssignmentResponse]
    traces: list[AssignmentTraceResponse]