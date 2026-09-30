from typing import Optional

from event_registration.application.ports import EventRepository, ParticipantRepository
from event_registration.domain.event import Event
from event_registration.domain.participant import Participant


class InMemoryEventRepository(EventRepository):
    """Stores Event aggregates (with their Registrations) in a dict keyed by event_id."""

    def __init__(self) -> None:
        self._store: dict[str, Event] = {}

    def get(self, event_id: str) -> Optional[Event]:
        return self._store.get(event_id)

    def save(self, event: Event) -> None:
        self._store[event.event_id] = event


class InMemoryParticipantRepository(ParticipantRepository):
    """Stores Participant aggregates in a dict keyed by participant_id."""

    def __init__(self) -> None:
        self._store: dict[str, Participant] = {}

    def get(self, participant_id: str) -> Optional[Participant]:
        return self._store.get(participant_id)

    def save(self, participant: Participant) -> None:
        self._store[participant.participant_id] = participant
