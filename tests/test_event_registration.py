"""T1-T8 for the Event Registration coursework.  Run: python -m unittest tests.test_event_registration -v"""
import unittest
from datetime import datetime

from event_registration.application.confirm_attendance import ConfirmAttendanceService
from event_registration.application.dispatcher import EventDispatcher
from event_registration.application.dtos import RegisterParticipantCommand
from event_registration.application.errors import EventNotFoundError, ParticipantNotFoundError
from event_registration.application.handlers import AttendanceConfirmationHandler
from event_registration.application.register_participant import RegisterParticipantService
from event_registration.domain.errors import (
    DuplicateRegistrationError, EventFullError, EventNotOpenError,
    InvalidEventStateError, InvalidTimeSlotError)
from event_registration.domain.event import Event
from event_registration.domain.events import ParticipantRegistered
from event_registration.domain.participant import Participant
from event_registration.domain.services import RegistrationFeeCalculator
from event_registration.domain.value_objects import TimeSlot
from event_registration.infrastructure.in_memory_repositories import (
    InMemoryEventRepository, InMemoryParticipantRepository)


def slot(h1: int, h2: int) -> TimeSlot:
    return TimeSlot(datetime(2026, 10, 10, h1), datetime(2026, 10, 10, h2))


class EventRegistrationTests(unittest.TestCase):
    def setUp(self):
        # Dependency injection: implementations are supplied to the services from outside.
        self.events = InMemoryEventRepository()
        self.participants = InMemoryParticipantRepository()
        self.dispatcher = EventDispatcher()
        self.confirm = ConfirmAttendanceService(self.events, self.participants)
        self.handler = AttendanceConfirmationHandler(self.confirm)
        self.dispatcher.subscribe(ParticipantRegistered, self.handler.handle)
        self.register = RegisterParticipantService(
            self.events, self.participants, RegistrationFeeCalculator(), self.dispatcher)

    # helpers
    def make_open_event(self, event_id="EV1", h1=9, h2=11, capacity=10, fee=20000):
        ev = Event(event_id, f"Event {event_id}", slot(h1, h2), capacity, fee)
        ev.open()
        self.events.save(ev)
        return ev

    def make_participant(self, pid="P1", student=False):
        p = Participant(pid, f"Name {pid}", student)
        self.participants.save(p)
        return p

    # ---------------------------------------------------------------- T1
    def test_T1_BR1_time_slot_must_end_after_it_starts(self):
        valid = slot(9, 11)                                   # accepted
        self.assertEqual(valid.end.hour, 11)
        with self.assertRaises(InvalidTimeSlotError):         # boundary: end == start
            TimeSlot(datetime(2026, 10, 10, 9), datetime(2026, 10, 10, 9))
        with self.assertRaises(InvalidTimeSlotError):         # rejection: end before start
            slot(11, 9)

    # ---------------------------------------------------------------- T2
    def test_T2_BR2_event_accepts_registration_only_when_open(self):
        ev = Event("EV1", "Draft event", slot(9, 11), capacity=5, base_fee=0)
        with self.assertRaises(EventNotOpenError):            # rejection: DRAFT
            ev.register("P1", 0)
        ev.open()
        ev.register("P1", 0)                                  # accepted: OPEN
        with self.assertRaises(InvalidEventStateError):       # rejection: cannot open twice
            ev.open()
        ev.close()
        with self.assertRaises(EventNotOpenError):            # rejection: CLOSED
            ev.register("P2", 0)

    # ---------------------------------------------------------------- T3
    def test_T3_BR3_event_never_exceeds_capacity_or_duplicates_participant(self):
        ev = Event("EV1", "Small event", slot(9, 11), capacity=2, base_fee=0)
        ev.open()
        ev.register("P1", 0)
        ev.register("P2", 0)                                  # boundary: exactly at capacity
        with self.assertRaises(EventFullError):               # rejection: one over capacity
            ev.register("P3", 0)
        self.assertEqual(len(ev.registrations), 2)
        ev2 = Event("EV2", "Dup event", slot(9, 11), capacity=5, base_fee=0)
        ev2.open()
        ev2.register("P1", 0)
        with self.assertRaises(DuplicateRegistrationError):   # rejection: same participant twice
            ev2.register("P1", 0)

    # ---------------------------------------------------------------- T4
    def test_T4_BR4_fee_depends_on_event_and_participant(self):
        calc = RegistrationFeeCalculator()
        ev = Event("EV1", "Paid", slot(9, 11), capacity=5, base_fee=20000)
        self.assertEqual(calc.calculate(ev, Participant("P1", "A", is_student=True)), 10000)
        self.assertEqual(calc.calculate(ev, Participant("P2", "B", is_student=False)), 20000)
        free = Event("EV2", "Free", slot(9, 11), capacity=5, base_fee=0)
        self.assertEqual(calc.calculate(free, Participant("P3", "C", is_student=True)), 0)

    # ---------------------------------------------------------------- T5
    def test_T5_BR5_registration_raises_event_and_handler_confirms_attendance(self):
        ev = self.make_open_event(capacity=1)
        p = self.make_participant("P1")
        ev.register("P1", 20000)
        raised = ev.pull_events()
        self.assertEqual(len(raised), 1)                      # event raised after acceptance
        self.assertIsInstance(raised[0], ParticipantRegistered)
        self.assertEqual((raised[0].event_id, raised[0].participant_id), ("EV1", "P1"))
        self.dispatcher.publish(raised)                       # handler -> Aggregate B
        self.assertTrue(p.has_confirmed("EV1"))
        with self.assertRaises(EventFullError):               # rejected registration ...
            ev.register("P2", 20000)
        self.assertEqual(ev.pull_events(), [])                # ... raises NO event

    # ---------------------------------------------------------------- T6
    def test_T6_BR6_aggregates_must_exist_before_registering(self):
        self.make_open_event("EV1")
        self.make_participant("P1")
        with self.assertRaises(EventNotFoundError):
            self.register.execute(RegisterParticipantCommand("NOPE", "P1"))
        with self.assertRaises(ParticipantNotFoundError):
            self.register.execute(RegisterParticipantCommand("EV1", "NOPE"))
        self.assertEqual(len(self.events.get("EV1").registrations), 0)   # nothing was changed

    # ---------------------------------------------------------------- T7
    def test_T7_main_use_case_success_event_handled_and_participant_updated(self):
        self.make_open_event("EV1", capacity=10, fee=20000)
        p = self.make_participant("P1", student=True)
        result = self.register.execute(RegisterParticipantCommand("EV1", "P1"))
        self.assertEqual(result.registration_id, "REG-EV1-1")
        self.assertEqual(result.fee, 10000)                   # BR4 applied
        self.assertTrue(result.attendance_confirmed)          # event handled, B accepted
        self.assertTrue(self.events.get("EV1").is_registered("P1"))   # Aggregate A changed
        self.assertTrue(p.has_confirmed("EV1"))                       # Aggregate B changed

    # ---------------------------------------------------------------- T8
    def test_T8_participant_rejects_follow_up_when_schedule_clashes(self):
        self.make_open_event("EV1", h1=9, h2=11)
        self.make_open_event("EV2", h1=10, h2=12)             # overlaps EV1
        p = self.make_participant("P1")
        first = self.register.execute(RegisterParticipantCommand("EV1", "P1"))
        self.assertTrue(first.attendance_confirmed)
        second = self.register.execute(RegisterParticipantCommand("EV2", "P1"))
        # returned outcome
        self.assertTrue(second.registration_id.startswith("REG-EV2"))
        self.assertFalse(second.attendance_confirmed)
        self.assertIn("Schedule conflict", second.message)
        # final state: B refused (only EV1 confirmed); A keeps the registration
        self.assertEqual(p.confirmed_event_ids, frozenset({"EV1"}))
        self.assertTrue(self.events.get("EV2").is_registered("P1"))


if __name__ == "__main__":
    unittest.main()
