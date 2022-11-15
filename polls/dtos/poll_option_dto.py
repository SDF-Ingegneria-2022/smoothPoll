class PollOptionDto:
    """
    Poll Option. One of the choices user may 
    choose from.
    """

    key: str 
    value: str

    def __init__(self, value: str, key: str=None) -> None:

        self.value = value
        self.key = key if key is not None else value
