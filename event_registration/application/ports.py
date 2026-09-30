"""Repository abstractions (one per aggregate root). Implemented in infrastructure."""
from abc import ABC, abstractmethod
from typing import Optional

from event_registration.domain.event import Event
from event_registration.domain.participant import Participant


class EventRepository(ABC):
    @abstractmethod
    def get(self, event_id: str) -> Optional[Event]: ...
    @abstractmethod
    def save(self, event: Event) -> None: ...


class ParticipantRepository(ABC):
    @abstractmethod
    def get(self, participant_id: str) -> Optional[Participant]: ...
    @abstractmethod
    def save(self, participant: Participant) -> None: ...
