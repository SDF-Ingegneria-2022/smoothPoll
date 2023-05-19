import abc
from typing import List
from apps.polls_management.models.majority_vote_model import MajorityVoteModel

from apps.polls_management.models.poll_model import PollModel
from apps.votes_results.classes.majority_poll_result_data import MajorityPollResultData


class IMajorityJudgmentResults(abc.ABC):
    """The expected schema for Majority Judgment voting
      results. It provides a method to calculate the results
      + some information getters that will be used in template"""


    def __init__(self, poll: PollModel) -> None:
        self.poll = poll  

    @abc.abstractmethod
    def calculate(self) -> None:
        """Do once the calculation of the results and store all
        information locally (so you avoid to repeat DB queries 
        and heavy calculations)"""
        pass

    @abc.abstractmethod
    def get_votes(self) -> List[MajorityVoteModel]:
        """Return the list of all submitted votes."""
        pass

    @abc.abstractmethod
    def get_sorted_options(self) -> List[List[MajorityPollResultData]]:
        """The actual sorted algorithm results, from the better option
        to the worse. We use a list of list because there could be equal 
        scores."""
        pass

    def get_sorted_options_no_parity(self) -> List[MajorityPollResultData]:

        res = self.get_sorted_options()
        
        poll_results: List[MajorityPollResultData] = []
        for p in res:
            for r in p:
                poll_results.append(r)

        return poll_results
        
