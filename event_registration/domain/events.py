from dataclasses import dataclass

from .base import DomainEvent


@dataclass(frozen=True)
class ParticipantRegistered(DomainEvent):
    """BR5 - raised by the Event aggregate AFTER a registration was accepted."""
    event_id: str
    participant_id: str
    registration_id: str
