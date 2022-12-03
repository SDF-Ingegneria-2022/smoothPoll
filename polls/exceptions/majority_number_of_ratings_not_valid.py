class MajorityNumberOfRatingsNotValid(Exception):
    """
    A number of ratings is unvalid for a certain poll option
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


