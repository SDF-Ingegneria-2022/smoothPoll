class ResultsNotAvailableException(Exception):
    """Exception raised when results are not available."""
    def __init__(self, message=None):
        self.message = "Results are not availble." if message is None else message
        super().__init__(self.message)