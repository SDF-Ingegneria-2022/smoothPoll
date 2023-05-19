from typing import List
from apps.polls_management.models.majority_vote_model import MajorityVoteModel
from apps.votes_results.classes.majority_judgment_results.i_majority_judment_results import IMajorityJudgmentResults
from apps.votes_results.classes.majority_poll_result_data import MajorityPollResultData


class ParityMJResults(IMajorityJudgmentResults):

    def calculate(self) -> None:
        
        # -------------------------------------
        # save votes
        self.__votes = MajorityVoteModel.objects.filter(
            poll=self.poll)
        
        # -------------------------------------
        # compute results

        options: List[MajorityPollResultData] = []

        # calculate triplets <#worst votes, median(sign), #best votes> 
        # foreach option
        for option in self.poll.options():
            options.append(
                MajorityPollResultData(option)
                )
        
        # sort
        options.sort(reverse=True)

        # create positions
        positions = [[options[0]]]

        for o in options[1:]:
            if o.compare(positions[-1][0]) == 0:
                positions[-1].append(o)
            else:
                positions.append([o])

        # TODO: implement manually a sorting algorithm which 
        # takes into account the parity of the votes
        self.__sorted_options = positions   
    
    def get_votes(self) -> List[MajorityVoteModel]:
        return self.__votes
    
    def get_sorted_options(self) -> List[List[MajorityPollResultData]]:
        return self.__sorted_options
    
        

    
