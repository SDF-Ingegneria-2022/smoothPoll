class PollNotValidCreationException(Exception):
    """
    A not valid poll creation was attempted.
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)
    

class MissingNameOrQuestionExcetion(PollNotValidCreationException):
    """You tried to create a poll without passing name or question"""

    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class PollOptionsNotValidExcetion(PollNotValidCreationException):
    """You tried to create a poll with something wrong in options"""

    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class TooManyOptionsExcetion(PollOptionsNotValidExcetion):
    """You tried to create a poll with too many options"""

    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class TooFewOptionsExcetion(PollOptionsNotValidExcetion):
    """You tried to create a poll with too few options"""

    def __init__(self, *args: object) -> None:
        super().__init__(*args)