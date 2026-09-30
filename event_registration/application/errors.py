class ApplicationError(Exception):
    pass


class EventNotFoundError(ApplicationError):         # BR6
    pass


class ParticipantNotFoundError(ApplicationError):   # BR6
    pass
