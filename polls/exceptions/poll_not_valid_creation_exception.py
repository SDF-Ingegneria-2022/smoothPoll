class PollNotValidCreationException(Exception):
    """
    A not valid poll creation was attempted.
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)
    