class WrongPollOptions(Exception):
    """
    Poll options don't belong to the same poll
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)
