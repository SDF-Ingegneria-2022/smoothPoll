class VoteDoesNotExistException(Exception):
    """
    A certain vote does not exists
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)