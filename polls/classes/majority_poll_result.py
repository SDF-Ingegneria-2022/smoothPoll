from dataclasses import dataclass
from typing import List
from polls.models.majority_option_model import MajorityOptionModel
from polls.models.poll_model import PollModel
from django.db.models import Max

from polls.models.poll_option_model import PollOptionModel

@dataclass
class MajorityPollResult:
    """Class where the result of the majority poll is calculated"""

    majority_poll: PollModel
    """
    The majority poll the result is about
    """
    poll_options: PollOptionModel
    """
    The poll options the majority poll is about
    """

    #remake in a better way
    def __init__(self, poll: PollModel) -> None:
        self.majority_poll: PollModel = poll
        self.poll_options: PollOptionModel = self.majority_poll.objects.filter(poll_fk=self.majority_poll.id)

    """Method used to return the median of the rating options"""
    def majority_median(self) -> int:
        rating_options: MajorityOptionModel = self.poll_options.objects.filter(poll_option=self.poll_options.id)
        max_rating: int = rating_options.objects.aggregate(Max('rating'))

        if max_rating % 2 == 0:
            return max_rating / 2
        else:
            return int(max_rating / 2)

    """Method used to count the good and bad ratings of the majority votes of one poll option"""
    def majority_count(majority_poll_option: PollOptionModel, median: int) -> tuple(int):

        all_options: MajorityOptionModel = majority_poll_option.objects.filter(poll_option=majority_poll_option.id)
        voted_options: MajorityOptionModel = all_options.objects.exclude(poll_vote__isnull=True)
        good_votes: int = int(0)
        bad_votes: int = int(0)

        for rating in voted_options:
            if rating.rating > median:
                good_votes += 1
            elif rating.rating < median:
                bad_votes += 1
        
        return (good_votes, median, bad_votes)

    """Method used to return a list of tuple of good, median and bad votes"""
    def print_result(results: List[tuple(int)]) -> List[tuple(int)]:

        # remake this in a simpler and better way
        for first in results:
            for second in results:
                if first != second and first[0] > first[2] and second[0] < second[2]:
                    first, second = second, first   # to check if the swap can be done like this or the index is necessary
                elif first != second and first[0] > first[2] and second[0] > second[2]:
                    if first[0] > second[0]:
                        first, second = second, first
                elif first != second and first[0] < first[2] and second[0] < second[2]:
                    if first[2] > second[2]:
                        first, second = second, first

        return results

