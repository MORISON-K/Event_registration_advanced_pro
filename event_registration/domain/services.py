from .event import Event
from .participant import Participant


class RegistrationFeeCalculator:
    """BR4 - Domain Service (cross-concept rule).

    The fee depends on the Event (base fee) AND the Participant (student status),
    so it belongs naturally to neither of them.
    """
    STUDENT_DIVISOR = 2      # students pay half

    def calculate(self, event: Event, participant: Participant) -> int:
        if participant.is_student:
            return event.base_fee // self.STUDENT_DIVISOR
        return event.base_fee
