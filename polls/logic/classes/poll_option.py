class PollOption:
    """
    Poll Option. One of the choices user may 
    choose from.
    """

    value: str

    def __init__(self, value: str) -> None:
        self.value = value