from .base import AggregateRoot
from .errors import ScheduleConflictError
from .value_objects import TimeSlot


class Participant(AggregateRoot):
    """AGGREGATE B - root: Participant (identity = participant_id).

    Invariant: the participant's confirmed attendances never overlap in time.
    This is the rule checked before accepting the BR5 follow-up action.
    """

    def __init__(self, participant_id: str, name: str, is_student: bool = False) -> None:
        super().__init__()
        self._participant_id = participant_id
        self._name = name
        self._is_student = is_student
        self._confirmed: dict[str, TimeSlot] = {}   # event_id -> slot

    @property
    def participant_id(self) -> str: return self._participant_id
    @property
    def name(self) -> str: return self._name
    @property
    def is_student(self) -> bool: return self._is_student
    @property
    def confirmed_event_ids(self) -> frozenset[str]: return frozenset(self._confirmed)

    def has_confirmed(self, event_id: str) -> bool:
        return event_id in self._confirmed

    def confirm_attendance(self, event_id: str, slot: TimeSlot) -> None:
        if event_id in self._confirmed:      # idempotent: confirming twice changes nothing
            return
        for other_id, other_slot in self._confirmed.items():
            if slot.overlaps(other_slot):
                raise ScheduleConflictError(
                    f"Schedule conflict: {event_id} overlaps already confirmed {other_id}")
        self._confirmed[event_id] = slot
