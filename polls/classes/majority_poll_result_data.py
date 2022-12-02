from polls.models.poll_option_model import PollOptionModel


class MajorityPollResultData:
    """Small class used to store the data related to
    the results of a majority poll"""

    poll_option_data: PollOptionModel
    """The poll_option the data is related to"""

    good_votes: int
    """The number of good votes performed to this option"""

    median: int
    """The majority grade of the option/poll, called as a median
    of the value of the votes"""

    bad_votes: int
    """The number of bad votes performed to this option"""

    positive_grade: bool
    """The majority grade sign is '+' if good votes are more than
    bad votes"""

    # negative_grade: bool
    # """The majority grade sign is '-' if bad votes are more than
    # good votes"""
    
    # def __init__(self, option: PollOptionModel, good: int, med: int, bad: int) -> None:
    #     self.poll_option_data = option
    #     self.good_votes = good
    #     self.median = med
    #     self.bad_votes = bad
    #     self.positive_grade = self.good_votes >= self.bad_votes
    #     self.negative_grade = self.good_votes < self.bad_votes
