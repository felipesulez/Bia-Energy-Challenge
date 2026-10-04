from dataclasses import dataclass

from assignment_engine.domain.assignment import Assignment
from assignment_engine.domain.assignment_trace import AssignmentTrace


@dataclass(frozen=True)
class AssignmentBatchResult:
    """
    Result of assigning a batch of records.

    Contains:
    - all assignment outcomes
    - all traces explaining those decisions

    This object represents a snapshot of one assignment execution.
    """

    assignments: tuple[Assignment, ...]
    traces: tuple[AssignmentTrace, ...]