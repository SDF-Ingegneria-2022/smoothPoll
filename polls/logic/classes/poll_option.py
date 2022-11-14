class PollOption:
    """
    Poll Option. One of the choices user may 
    choose from.
    """

    text: str 
    value: str

    def __init__(self, text: str, value: str=None) -> None:

        self.text = text
        self.value = value if value is not None else text
