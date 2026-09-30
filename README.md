# Event Registration - DDD, TDD and Clean Architecture (Python)

Domain: **Event registration**. Use case 1: *Register a participant for an event*.
Use case 2: *Confirm the participant's attendance*. They are connected by the
Domain Event `ParticipantRegistered`. Persistence is in-memory. Python 3.10+, standard library only.

## Run the tests
    python -m unittest tests.test_event_registration -v

Other commands: `python tools/check_dependencies.py` (layer dependency check),
`python -m event_registration.interface.cli` (demo).

## Business rules -> code -> test
| Rule | Type | Responsible component | On violation | Test |
|---|---|---|---|---|
| BR1 A time slot must end after it starts | Value | `TimeSlot` (Value Object) | `InvalidTimeSlotError` | T1 |
| BR2 An event accepts registrations only while OPEN (DRAFT->OPEN->CLOSED) | Identity/state | `Event` (Aggregate A root) | `EventNotOpenError` / `InvalidEventStateError` | T2 |
| BR3 An event never exceeds capacity and never registers a participant twice | Invariant | `Event` root guarding its `Registration` entities | `EventFullError` / `DuplicateRegistrationError` | T3 |
| BR4 Fee depends on event base fee AND participant (students pay half) | Cross-concept | `RegistrationFeeCalculator` (Domain Service) | n/a (calculation) | T4 |
| BR5 After a registration is accepted, attendance must be confirmed for the participant, who accepts only if there is no overlapping confirmed attendance | Follow-up | `ParticipantRegistered` -> `AttendanceConfirmationHandler` -> `Participant` (Aggregate B root) | `ScheduleConflictError` (reported, registration stays) | T5, T7, T8 |
| BR6 Event and participant must exist before registering | Lookup | Repositories + `RegisterParticipantService` | `EventNotFoundError` / `ParticipantNotFoundError` | T6 |

## Model summary
- Aggregate A: `Event` (root, id = `event_id`) with child entity `Registration` (id = `registration_id`). Invariant: BR3.
- Aggregate B: `Participant` (root, id = `participant_id`). Invariant: confirmed attendances never overlap.
- Value Object: `TimeSlot` (no identity, immutable, equal by value).
- Factory: **not used** - creation is a plain constructor with two trivial checks, not enough rules to justify one.
- Layer Supertype: **used** - `AggregateRoot` (domain/base.py) gives both roots the same event-recording code.

## Layers (dependencies point inward only)
    interface -> infrastructure -> application -> domain
- domain: entities, value object, roots, domain service, domain event, errors
- application: `RegisterParticipantService`, `ConfirmAttendanceService`, handler, dispatcher, DTOs, repository abstractions (`ports.py`)
- infrastructure: in-memory repositories
- interface: `composition.py` (dependency injection happens here) and `cli.py`

## Flow
Command DTO -> `RegisterParticipantService` -> `Event.register` (Aggregate A) -> `ParticipantRegistered`
-> `AttendanceConfirmationHandler` -> `ConfirmAttendanceService` -> `Participant.confirm_attendance` (Aggregate B) -> result DTO.

## Design choice changed (for Slide 14)
First idea: if Participant rejects the follow-up, cancel the registration in the Event. Changed: registration and attendance
confirmation are separate consistency boundaries, so the registration stands and the result reports
`attendance_confirmed=False` with the reason (T8). This keeps aggregates from modifying each other.

## Evidence files (evidence/)
`test_run_output.txt` (T1-T8 pass) - `tdd_1_failing.txt` (T3 red) - `tdd_2_passing.txt` (T3 green) -
`dependency_check_output.txt` - `demo_output.txt`

## AI use
Claude (Anthropic) helped draft the initial code and tests; the group reviewed and can explain every part.
