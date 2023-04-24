
class PollCannotBeClosedException(Exception):
    """
    A certain Poll cannot be closed for voting.
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)
