from event_registration.application.dispatcher import EventDispatcher
from event_registration.application.dtos import (
    ConfirmAttendanceResult, RegisterParticipantCommand, RegisterParticipantResult)
from event_registration.application.errors import EventNotFoundError, ParticipantNotFoundError
from event_registration.application.ports import EventRepository, ParticipantRepository
from event_registration.domain.services import RegistrationFeeCalculator


class RegisterParticipantService:
    """USE CASE 1 - Register a participant for an event (the MAIN use case).

    Dependencies are injected through the constructor (dependency injection).
    The service contains NO business rules: it looks things up (BR6), asks the
    domain service for the fee (BR4), asks the aggregate to register (BR2/BR3),
    saves, and publishes the domain events (BR5).
    """

    def __init__(self, events: EventRepository, participants: ParticipantRepository,
                 fee_calculator: RegistrationFeeCalculator, dispatcher: EventDispatcher) -> None:
        self._events = events
        self._participants = participants
        self._fees = fee_calculator
        self._dispatcher = dispatcher

    def execute(self, cmd: RegisterParticipantCommand) -> RegisterParticipantResult:
        event = self._events.get(cmd.event_id)                      # BR6
        if event is None:
            raise EventNotFoundError(f"Event {cmd.event_id} not found")
        participant = self._participants.get(cmd.participant_id)    # BR6
        if participant is None:
            raise ParticipantNotFoundError(f"Participant {cmd.participant_id} not found")

        fee = self._fees.calculate(event, participant)              # BR4
        registration = event.register(participant.participant_id, fee)   # BR2, BR3
        self._events.save(event)

        outcomes = self._dispatcher.publish(event.pull_events())    # BR5
        confirmation = next((o for o in outcomes if isinstance(o, ConfirmAttendanceResult)), None)
        confirmed = bool(confirmation and confirmation.confirmed)
        message = "Registered; attendance confirmed" if confirmed else (
            f"Registered; attendance NOT confirmed: {confirmation.message}" if confirmation
            else "Registered")
        return RegisterParticipantResult(registration.registration_id, event.event_id,
                                         participant.participant_id, fee, confirmed, message)
