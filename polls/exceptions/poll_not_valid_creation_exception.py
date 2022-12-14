class PollNotValidCreationException(Exception):
    """
    A not valid poll creation was attempted.
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)
    

class NameOrQuestionNotValidException(PollNotValidCreationException):
    """You tried to create a poll without passing a valid 
    name or question through form. Reasons may be many."""

    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class PollOptionsNotValidException(PollNotValidCreationException):
    """You tried to create a poll with something wrong in options"""

    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class TooManyOptionsException(PollOptionsNotValidException):
    """You tried to create a poll with too many options"""

    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class TooFewOptionsException(PollOptionsNotValidException):
    """You tried to create a poll with too few options"""

    def __init__(self, *args: object) -> None:
        super().__init__(*args)