from event_registration.application.dtos import ConfirmAttendanceCommand, ConfirmAttendanceResult
from event_registration.application.errors import EventNotFoundError, ParticipantNotFoundError
from event_registration.application.ports import EventRepository, ParticipantRepository


class ConfirmAttendanceService:
    """USE CASE 2 - Confirm the participant's attendance.
    Coordinates only: lookups (BR6), then the domain does the rule checking."""

    def __init__(self, events: EventRepository, participants: ParticipantRepository) -> None:
        self._events = events
        self._participants = participants

    def execute(self, cmd: ConfirmAttendanceCommand) -> ConfirmAttendanceResult:
        participant = self._participants.get(cmd.participant_id)
        if participant is None:
            raise ParticipantNotFoundError(f"Participant {cmd.participant_id} not found")
        event = self._events.get(cmd.event_id)
        if event is None:
            raise EventNotFoundError(f"Event {cmd.event_id} not found")

        event.ensure_registered(participant.participant_id)          # domain rule
        participant.confirm_attendance(event.event_id, event.slot)   # domain rule (BR5 check)
        self._participants.save(participant)
        return ConfirmAttendanceResult(participant.participant_id, event.event_id, True,
                                       "Attendance confirmed")
