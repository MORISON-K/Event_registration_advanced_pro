from collections import defaultdict
from typing import Any, Callable

from event_registration.domain.base import DomainEvent


class EventDispatcher:
    """Simple in-process domain-event dispatcher."""

    def __init__(self) -> None:
        self._handlers: dict[type, list[Callable[[Any], Any]]] = defaultdict(list)

    def subscribe(self, event_type: type, handler: Callable[[Any], Any]) -> None:
        self._handlers[event_type].append(handler)

    def publish(self, events: list[DomainEvent]) -> list[Any]:
        results = []
        for event in events:
            for handler in self._handlers[type(event)]:
                results.append(handler(event))
        return results
