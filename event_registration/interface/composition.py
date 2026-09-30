"""Composition root: the ONLY place where concrete classes are chosen and injected."""
from dataclasses import dataclass

from event_registration.application.confirm_attendance import ConfirmAttendanceService
from event_registration.application.dispatcher import EventDispatcher
from event_registration.application.handlers import AttendanceConfirmationHandler
from event_registration.application.register_participant import RegisterParticipantService
from event_registration.domain.events import ParticipantRegistered
from event_registration.domain.services import RegistrationFeeCalculator
from event_registration.infrastructure.in_memory_repositories import (
    InMemoryEventRepository, InMemoryParticipantRepository)


@dataclass
class Container:
    events: InMemoryEventRepository
    participants: InMemoryParticipantRepository
    register_participant: RegisterParticipantService
    confirm_attendance: ConfirmAttendanceService


def build_container() -> Container:
    events = InMemoryEventRepository()
    participants = InMemoryParticipantRepository()
    dispatcher = EventDispatcher()
    confirm = ConfirmAttendanceService(events, participants)
    dispatcher.subscribe(ParticipantRegistered, AttendanceConfirmationHandler(confirm).handle)
    register = RegisterParticipantService(events, participants, RegistrationFeeCalculator(), dispatcher)
    return Container(events, participants, register, confirm)
