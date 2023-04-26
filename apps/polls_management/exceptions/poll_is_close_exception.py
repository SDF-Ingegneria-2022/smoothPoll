class PollIsCloseException(Exception):
    """
    A certain Poll is already close
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)
