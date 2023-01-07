class NotSingleOptionPollException(Exception):
    """Exception raised when a poll is not a single option poll."""
    def __init__(self):
        self.message = "Poll is not a single option poll."
        super().__init__(self.message)