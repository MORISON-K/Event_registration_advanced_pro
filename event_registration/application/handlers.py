from event_registration.application.confirm_attendance import ConfirmAttendanceService
from event_registration.application.dtos import ConfirmAttendanceCommand, ConfirmAttendanceResult
from event_registration.domain.errors import DomainError
from event_registration.domain.events import ParticipantRegistered


class AttendanceConfirmationHandler:
    """BR5 handler: reacts to ParticipantRegistered by requesting attendance
    confirmation in Aggregate B (Participant). Aggregate B decides; if it rejects,
    the handler reports the outcome instead of modifying anything itself."""

    def __init__(self, confirm_service: ConfirmAttendanceService) -> None:
        self._confirm = confirm_service

    def handle(self, event: ParticipantRegistered) -> ConfirmAttendanceResult:
        try:
            return self._confirm.execute(
                ConfirmAttendanceCommand(event.participant_id, event.event_id))
        except DomainError as error:
            return ConfirmAttendanceResult(event.participant_id, event.event_id, False, str(error))
