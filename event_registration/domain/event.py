from enum import Enum

from .base import AggregateRoot
from .errors import (
    DuplicateRegistrationError,
    EventFullError,
    EventNotOpenError,
    InvalidEventError,
    InvalidEventStateError,
    NotRegisteredError,
)
from .events import ParticipantRegistered
from .value_objects import TimeSlot


class EventStatus(Enum):
    DRAFT = "DRAFT"
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class Registration:
    """Entity (child of Event). Identity = registration_id."""

    def __init__(self, registration_id: str, participant_id: str, fee: int) -> None:
        self.registration_id = registration_id
        self.participant_id = participant_id
        self.fee = fee

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Registration) and other.registration_id == self.registration_id

    def __hash__(self) -> int:
        return hash(self.registration_id)


class Event(AggregateRoot):
    """AGGREGATE A - root: Event (identity = event_id).

    BR2 (state rule): DRAFT -> OPEN -> CLOSED; registration only while OPEN.
    BR3 (invariant): registrations never exceed capacity and a participant
        is registered at most once. Only the root changes its Registrations.
    """

    def __init__(self, event_id: str, title: str, slot: TimeSlot, capacity: int,
                 base_fee: int = 0, status: EventStatus = EventStatus.DRAFT) -> None:
        super().__init__()
        if capacity < 1:
            raise InvalidEventError("Capacity must be at least 1")
        if base_fee < 0:
            raise InvalidEventError("Base fee cannot be negative")
        self._event_id = event_id
        self._title = title
        self._slot = slot
        self._capacity = capacity
        self._base_fee = base_fee
        self._status = status
        self._registrations: list[Registration] = []

    # ---- read access ----
    @property
    def event_id(self) -> str: return self._event_id
    @property
    def title(self) -> str: return self._title
    @property
    def slot(self) -> TimeSlot: return self._slot
    @property
    def capacity(self) -> int: return self._capacity
    @property
    def base_fee(self) -> int: return self._base_fee
    @property
    def status(self) -> EventStatus: return self._status
    @property
    def registrations(self) -> tuple[Registration, ...]: return tuple(self._registrations)

    def is_registered(self, participant_id: str) -> bool:
        return any(r.participant_id == participant_id for r in self._registrations)

    def ensure_registered(self, participant_id: str) -> None:
        if not self.is_registered(participant_id):
            raise NotRegisteredError(
                f"Participant {participant_id} is not registered for event {self._event_id}")

    # ---- BR2: state transitions ----
    def open(self) -> None:
        if self._status is not EventStatus.DRAFT:
            raise InvalidEventStateError(f"Only a DRAFT event can be opened (is {self._status.value})")
        self._status = EventStatus.OPEN

    def close(self) -> None:
        if self._status is not EventStatus.OPEN:
            raise InvalidEventStateError(f"Only an OPEN event can be closed (is {self._status.value})")
        self._status = EventStatus.CLOSED

    # ---- BR2 + BR3 + raises BR5 event ----
    def register(self, participant_id: str, fee: int) -> Registration:
        if self._status is not EventStatus.OPEN:
            raise EventNotOpenError(
                f"Event {self._event_id} is {self._status.value}; registration needs OPEN")
        if self.is_registered(participant_id):
            raise DuplicateRegistrationError(
                f"Participant {participant_id} is already registered for {self._event_id}")
        if len(self._registrations) >= self._capacity:
            raise EventFullError(
                f"Event {self._event_id} is full (capacity {self._capacity})")
        registration = Registration(
            f"REG-{self._event_id}-{len(self._registrations) + 1}", participant_id, fee)
        self._registrations.append(registration)
        self._record(ParticipantRegistered(
            self._event_id, participant_id, registration.registration_id))
        return registration
