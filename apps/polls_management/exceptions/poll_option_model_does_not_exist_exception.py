class PollOptionDoesNotExist(Exception):
    """
    A certain Poll Option does not exist
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)
