"""Layer Supertype for the domain layer (USED - see README).

AggregateRoot gives every aggregate root the same event-recording behaviour,
so Event and Participant do not repeat it.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class DomainEvent:
    """Marker base class for all domain events."""


class AggregateRoot:
    def __init__(self) -> None:
        self._domain_events: list[DomainEvent] = []

    def _record(self, event: DomainEvent) -> None:
        self._domain_events.append(event)

    def pull_events(self) -> list[DomainEvent]:
        events, self._domain_events = self._domain_events, []
        return events
