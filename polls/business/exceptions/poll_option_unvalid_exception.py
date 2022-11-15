class PollOptionUnvalidException(Exception):
    """
    A PollOption is unvalid for a certain Poll
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)
    