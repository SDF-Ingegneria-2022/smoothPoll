class PollOptionRatingUnvalidException(Exception):
    """
    A poll option rating is unvalid for a certain Poll
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)
    