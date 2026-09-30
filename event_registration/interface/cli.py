"""Minimal entry point. Run:  python -m event_registration.interface.cli"""
from datetime import datetime

from event_registration.application.dtos import RegisterParticipantCommand
from event_registration.domain.event import Event
from event_registration.domain.participant import Participant
from event_registration.domain.value_objects import TimeSlot
from event_registration.interface.composition import build_container


def main() -> None:
    app = build_container()
    day = lambda h1, h2: TimeSlot(datetime(2026, 10, 10, h1), datetime(2026, 10, 10, h2))

    for eid, title, slot in (("EV1", "AI Workshop", day(9, 11)), ("EV2", "DDD Seminar", day(10, 12))):
        ev = Event(eid, title, slot, capacity=2, base_fee=20000)
        ev.open()
        app.events.save(ev)
    app.participants.save(Participant("P1", "Aisha", is_student=True))

    for eid in ("EV1", "EV2"):
        r = app.register_participant.execute(RegisterParticipantCommand(eid, "P1"))
        print(f"{eid}: {r}")


if __name__ == "__main__":
    main()
