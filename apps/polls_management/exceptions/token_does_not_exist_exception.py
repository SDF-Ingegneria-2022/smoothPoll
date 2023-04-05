class TokenDoesNotExistException(Exception):
    """
    A certain token does not exist.
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)
