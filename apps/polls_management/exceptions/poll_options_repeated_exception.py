class PollOptionsRepeated(Exception):
    """
    Poll options and input number are mismatched
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)
