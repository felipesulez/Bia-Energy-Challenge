from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import (
    get_assignment_history_context,
    get_execute_context,
    get_preview_context,
    get_reassign_context,
)

from app.mappers import to_preview_response

from app.schemas.assignment import (
    AssignmentDetailResponse,
    AssignmentExecuteRequest,
    AssignmentHistoryListResponse,
    AssignmentPreviewRequest,
    AssignmentPreviewResponse,
    AssignmentReassignRequest,
)


router = APIRouter(
    prefix="/assignments",
    tags=["assignments"],
)


@router.get(
    "",
    response_model=AssignmentHistoryListResponse,
)
def get_assignments(
    service=Depends(get_assignment_history_context),
):
    assignments = service.list_assignments()

    return {
        "assignments": assignments,
        "total": len(assignments),
    }


@router.get(
    "/{assignment_id}",
    response_model=AssignmentDetailResponse,
)
def get_assignment(
    assignment_id: int,
    service=Depends(get_assignment_history_context),
):
    assignment = service.get_assignment(assignment_id)

    if assignment is None:
        raise HTTPException(
            status_code=404,
            detail="Assignment not found.",
        )

    return assignment


@router.post(
    "/{assignment_id}/reassign",
    response_model=AssignmentDetailResponse,
)
def reassign_assignment(
    assignment_id: int,
    request: AssignmentReassignRequest,
    context=Depends(get_reassign_context),
):
    service, users, records, absences = context

    assignment = service.get_assignment(assignment_id)

    if assignment is None:
        raise HTTPException(
            status_code=404,
            detail="Assignment not found.",
        )

    record = next(
        (
            record
            for record in records
            if record.id == assignment["record_id"]
        ),
        None,
    )

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Record not found.",
        )

    try:
        service.reassign_record(
            record=record,
            users=users,
            absences=absences,
            evaluation_date=request.evaluation_date,
            executed_by=request.executed_by,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    active_assignment = next(
        (
            assignment
            for assignment in service.list_assignments()
            if (
                assignment["record_id"] == record.id
                and assignment["es_activa"] is True
            )
        ),
        None,
    )

    if active_assignment is None:
        raise HTTPException(
            status_code=500,
            detail="Reassigned assignment could not be retrieved.",
        )

    return active_assignment


@router.post(
    "/preview",
    response_model=AssignmentPreviewResponse,
)
def preview_assignments(
    request: AssignmentPreviewRequest,
    context=Depends(get_preview_context),
):
    service, users, records, absences = context

    result = service.preview_pending_records(
        records=records,
        users=users,
        absences=absences,
        evaluation_date=request.evaluation_date,
    )

    return to_preview_response(result)


@router.post(
    "/execute",
    response_model=AssignmentPreviewResponse,
)
def execute_assignments(
    request: AssignmentExecuteRequest,
    context=Depends(get_execute_context),
):
    service, users, records, absences = context

    result = service.execute_pending_records(
        records=records,
        users=users,
        absences=absences,
        evaluation_date=request.evaluation_date,
        executed_by=request.executed_by,
    )

    return to_preview_response(result)