from fastapi import APIRouter, Depends

from app.dependencies import (
    get_assignment_history_context,
    get_execute_context,
    get_preview_context,
)
from app.mappers import to_preview_response
from app.schemas.assignment import (
    AssignmentExecuteRequest,
    AssignmentHistoryListResponse,
    AssignmentPreviewRequest,
    AssignmentPreviewResponse,
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