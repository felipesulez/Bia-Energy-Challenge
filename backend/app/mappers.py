from assignment_engine.domain.assignment_batch_result import (
    AssignmentBatchResult,
)

from app.schemas.assignment import (
    AssignmentPreviewResponse,
    AssignmentResponse,
    AssignmentTraceResponse,
    CandidateResponse,
)


def to_preview_response(
    result: AssignmentBatchResult,
) -> AssignmentPreviewResponse:
    assignments = [
        AssignmentResponse(
            record_id=assignment.record_id,
            usuario_id=assignment.usuario_id,
            usuario_nombre=assignment.usuario_nombre,
            metodo=assignment.metodo,
            score_zona=assignment.score_zona,
            score_carga=assignment.score_carga,
            score_total=assignment.score_total,
            carga_antes=assignment.carga_antes,
            carga_despues=assignment.carga_despues,
            capacidad_antes=assignment.capacidad_antes,
            capacidad_despues=assignment.capacidad_despues,
            utilizacion_antes=assignment.utilizacion_antes,
            coincidencia_zona=assignment.coincidencia_zona,
            fallback_geografico=assignment.fallback_geografico,
            estado_geografico=assignment.estado_geografico,
            explicacion_zona=assignment.explicacion_zona,
            razon=assignment.razon,
        )
        for assignment in result.assignments
    ]

    traces = [
        AssignmentTraceResponse(
            record_id=trace.record_id,
            metodo=trace.metodo,
            candidatos=[
                CandidateResponse(
                    usuario_id=candidate.usuario_id,
                    nombre=candidate.nombre,
                    score_zona=candidate.score_zona,
                    score_carga=candidate.score_carga,
                    score_total=candidate.score_total,
                    carga_actual=candidate.carga_actual,
                    capacidad_disponible=candidate.capacidad_disponible,
                    utilizacion=candidate.utilizacion,
                )
                for candidate in trace.candidatos
            ],
            usuario_seleccionado_id=trace.usuario_seleccionado_id,
            criterio_seleccion=trace.criterio_seleccion,
            criterio_desempate=trace.criterio_desempate,
            estado_geografico=trace.estado_geografico,
            coincidencia_zona=trace.coincidencia_zona,
            fallback_geografico=trace.fallback_geografico,
            explicacion_zona=trace.explicacion_zona,
            razon=trace.razon,
            parametros=trace.parametros,
            ejecutado_por=trace.ejecutado_por,
            ejecutado_en=trace.ejecutado_en,
            reemplaza_assignment_id=trace.reemplaza_assignment_id,
            prompt=trace.prompt,
            respuesta_modelo=trace.respuesta_modelo,
        )
        for trace in result.traces
    ]

    return AssignmentPreviewResponse(
        assignments=assignments,
        traces=traces,
    )