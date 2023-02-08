class NoUserPollsException(Exception):
    """
    There are no polls created from this user.
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)
