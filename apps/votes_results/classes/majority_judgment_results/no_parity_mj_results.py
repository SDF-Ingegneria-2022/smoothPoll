

from typing import List
from apps.polls_management.models.majority_vote_model import MajorityVoteModel
from apps.votes_results.classes.majority_judgment_results.i_majority_judment_results import IMajorityJudgmentResults
from apps.votes_results.classes.majority_poll_result_data import MajorityPollResultData


class NoParityMJResults(IMajorityJudgmentResults):

    def calculate(self) -> None:
        
        # -------------------------------------
        # save votes
        self.__votes = MajorityVoteModel.objects.filter(
            poll=self.poll)
        
        # -------------------------------------
        # compute results

        results: List[MajorityPollResultData] = []

        # calculate triplet <#worst votes, median(sign), #best votes> foreach option
        for option in self.poll.options():
            option_result = MajorityPollResultData(option)
            results.append(option_result)

        # sort result (descendant)
        results.sort(reverse=True)
        self.__sorted_options = [[o] for o in results]
    
    def get_votes(self) -> List[MajorityVoteModel]:
        return self.__votes
    
    def get_sorted_options(self) -> List[List[MajorityPollResultData]]:
        return self.__sorted_options