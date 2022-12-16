class PollNotYetVodedException(Exception):
    """Poll did't received any vote and 
    you are trying to perform an operation 
    that needs at least one vote"""
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
