class NoVotableOrClosedPollException(Exception):
    """
    There are no polls that are votable or closed.
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)
