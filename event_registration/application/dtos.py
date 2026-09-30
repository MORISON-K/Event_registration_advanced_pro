from dataclasses import dataclass


@dataclass(frozen=True)
class RegisterParticipantCommand:          # INPUT DTO (use case 1)
    event_id: str
    participant_id: str


@dataclass(frozen=True)
class RegisterParticipantResult:           # OUTPUT DTO (use case 1)
    registration_id: str
    event_id: str
    participant_id: str
    fee: int
    attendance_confirmed: bool
    message: str


@dataclass(frozen=True)
class ConfirmAttendanceCommand:            # INPUT DTO (use case 2)
    participant_id: str
    event_id: str


@dataclass(frozen=True)
class ConfirmAttendanceResult:             # OUTPUT DTO (use case 2)
    participant_id: str
    event_id: str
    confirmed: bool
    message: str
