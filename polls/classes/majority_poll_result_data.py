
from polls.models.poll_option_model import PollOptionModel


class MajorityPollResultData:
    """Small class used to store the data related to
    the results of a majority poll"""

    poll_option_data: PollOptionModel

    good_votes: int

    median: int

    bad_votes: int

    def __init__(self, option: PollOptionModel, good: int, med: int, bad: int) -> None:
        self.poll_option_data = option
        self.good_votes = good
        self.median = med
        self.bad_votes = bad
