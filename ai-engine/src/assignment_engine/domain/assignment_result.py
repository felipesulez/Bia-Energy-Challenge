from dataclasses import dataclass

from assignment_engine.domain.assignment import Assignment
from assignment_engine.domain.assignment_trace import AssignmentTrace


@dataclass(frozen=True)
class AssignmentResult:
    """
    Result of an assignment operation.

    Contains both:
    - the assignment outcome
    - the trace explaining how the decision was reached

    This object does not perform assignment logic
    or modify application state.
    """

    assignment: Assignment
    trace: AssignmentTrace