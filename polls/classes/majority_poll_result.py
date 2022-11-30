from dataclasses import dataclass
from typing import List
from polls.models.majority_judgment_model import MajorityJudgmentModel
from polls.models.majority_vote_model import MajorityVoteModel
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

    #remake in a better way
    def __init__(self, poll: PollModel, poll_op: PollOptionModel) -> None:
        self.majority_poll: PollModel = poll

    """Method used to return the median of the rating options"""
    def majority_median(num:int) -> int:

        if num % 2 == 0:
            return num / 2
        else:
            return int(num / 2)

    """Method used to count the good and bad ratings of the majority votes of one poll option"""
    def majority_count(self, median_number) -> List[List[int]]:

        all_options: PollOptionModel = self.majority_poll.objects.filter(poll_fk=self.majority_poll.id)
        all_voted_options: List[MajorityJudgmentModel] = MajorityVoteModel.objects.get(poll=self.majority_poll.id).judgments()

        majority_count_votes: List[List[int]] = []

        for option in all_options:

            # to write it better (we need a list of MajorityJudgmentModel VOTED for a single option of the poll)
            option_votes: List[MajorityJudgmentModel] = all_voted_options.filter(poll_option=option.id)

            good_votes: int = int(0)
            bad_votes: int = int(0)

            for rating in option_votes:
                if rating.rating > median_number:
                    good_votes += 1
                elif rating.rating < median_number:
                    bad_votes += 1
        
            majority_count_votes.append([good_votes, median_number, bad_votes])

        return majority_count_votes

    """Method used to return a list of Tuple of good, median and bad votes"""
    def print_result(results: List[List[int]]) -> List[List[int]]:

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

