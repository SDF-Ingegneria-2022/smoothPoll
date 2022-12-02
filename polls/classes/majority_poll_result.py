from dataclasses import dataclass
from functools import cmp_to_key
from typing import List
from polls.classes.majority_poll_result_data import MajorityPollResultData
from polls.models.majority_judgment_model import MajorityJudgmentModel
from polls.models.majority_vote_model import MajorityVoteModel
from polls.models.poll_model import PollModel

from polls.models.poll_option_model import PollOptionModel

@dataclass
class MajorityPollResult:
    """Class where the result of the majority poll is calculated"""

    majority_poll: PollModel
    """
    The majority poll the result is about
    """

    #remake in a better way
    def __init__(self, poll: PollModel) -> None:
        self.majority_poll: PollModel = poll

    """Method used to return the median of the rating options"""
    def majority_median(self, num:int) -> int:

        if num % 2 == 0:
            return num / 2
        else:
            return int(num / 2)

    """Method used to count the good and bad ratings of the majority votes of one poll option"""
    def majority_count(self, median_number) -> List[MajorityPollResultData]:

        all_options: PollOptionModel = PollOptionModel.objects.filter(poll_fk=self.majority_poll.id)
        #votes: MajorityVoteModel = MajorityVoteModel.objects.filter(poll=self.majority_poll.id)

        majority_count_votes: List[MajorityPollResultData] = []

        for option in all_options:

            # to write it better (we need a list of MajorityJudgmentModel VOTED for a single option of the poll)
            # check here to see if the votes are really filtered by single option
            option_votes: MajorityJudgmentModel = MajorityJudgmentModel.objects.filter(poll_option=option.id)

            good_votes: int = int(0)
            bad_votes: int = int(0)

            for rating in option_votes:
                if rating.rating > median_number:
                    good_votes += 1
                elif rating.rating < median_number:
                    bad_votes += 1
        
            result_data: MajorityPollResultData = MajorityPollResultData(option, good_votes, median_number, bad_votes)

            majority_count_votes.append(result_data)

        return majority_count_votes

    """Method used to return a list of  of good, median and bad votes"""
    def vote_result(self, results: List[MajorityPollResultData]) -> List[MajorityPollResultData]:

        results_temp = results.copy()

        def compare(x, y):
            
            # if median is greater --> x win
            if x.median > y.median:
                return 1
            elif x.median < y.median:
                return -1

            # positive grade should win against  
            # negative grade
            if x.positive_grade and not y.positive_grade:
                return 1
            elif not x.positive_grade and y.positive_grade:
                return -1 
            
            # if both are positive, it wins who has greater number of 
            # strictly better votes
            if x.positive_grade and y.positive_grade:
                return 1 if x.good_votes > y.good_votes else -1
            elif (not x.positive_grade) and (not y.positive_grade):
                return 1 if x.bad_votes < y.bad_votes else -1

            return 0

        results_temp = sorted(results, key=cmp_to_key(compare), reverse=True)

        return results_temp

        # #remake this in a simpler and better way
        # for first in results:
        #     for second in results:
        #         if second.positive_grade and first.negative_grade:
        #             first, second = second, first   # to check if the swap can be done like this or the index is necessary
        #         elif second.positive_grade and first.positive_grade:
        #             if second.good_votes >= first.good_votes:
        #                 first, second = second, first
        #         elif second.negative_grade and first.negative_grade:
        #             if second.bad_votes >= first.bad_votes:
        #                 first, second = second, first

        # return results
