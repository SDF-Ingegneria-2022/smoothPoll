class PollCannotBeOpenedException(Exception):
    """
    A certain Poll cannot be opened for voting.
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)
