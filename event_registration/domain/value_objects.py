from dataclasses import dataclass
from datetime import datetime

from .errors import InvalidTimeSlotError


@dataclass(frozen=True)
class TimeSlot:
    """BR1 - Value rule: a time slot is valid only if it ends AFTER it starts.

    No identity: two slots with the same start and end are interchangeable,
    and the object is immutable (frozen).
    """
    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        if self.end <= self.start:
            raise InvalidTimeSlotError(
                f"Slot must end after it starts (start={self.start}, end={self.end})"
            )

    def overlaps(self, other: "TimeSlot") -> bool:
        # Slots that merely touch (one ends when the other starts) do NOT overlap.
        return self.start < other.end and other.start < self.end
