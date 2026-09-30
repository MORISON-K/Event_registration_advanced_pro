class DomainError(Exception):
    """Base class for every business-rule violation."""


class InvalidTimeSlotError(DomainError):        # BR1
    pass


class InvalidEventError(DomainError):
    pass


class EventNotOpenError(DomainError):           # BR2
    pass


class InvalidEventStateError(DomainError):      # BR2
    pass


class EventFullError(DomainError):              # BR3
    pass


class DuplicateRegistrationError(DomainError):  # BR3
    pass


class ScheduleConflictError(DomainError):       # BR5 (checked by Participant)
    pass


class NotRegisteredError(DomainError):          # UC2 precondition
    pass
