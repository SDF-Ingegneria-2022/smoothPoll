import abc
from typing import List
from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.models.poll_option_model import PollOptionModel
from apps.polls_management.models.schulze_vote_model import SchulzeVoteModel


class ISchulzeResults(abc.ABC):
    """The expected schema for Schulze voting results. It 
    provides a method to calculate the results + some information 
    getters that will be used in template to render results.
    
    It is the type expected by the Schulze results service."""

    def __init__(self, poll: PollModel) -> None:
        self.poll = poll        

    @abc.abstractmethod
    def calculate(self) -> None:
        """Do once the calculation of the results and store all
        information locally (so you avoid to repeat DB queries 
        and heavy calculations)"""
        pass

    @abc.abstractmethod
    def get_votes(self) -> List[SchulzeVoteModel]:
        """Return the list of all submitted votes."""
        pass

    @abc.abstractmethod
    def get_sorted_options(self) -> List[List[PollOptionModel]]:
        """The actual sorted algorithm results, from the better option
        to the worse. We use a list of list because there could be equal 
        scores."""
        pass

    def get_preference_matrix_cell(self, a: PollOptionModel, b: PollOptionModel) -> List[int]:
        """Return the number of times a is prefered to b."""

        if a == b:
            return "/"

        count = 0
        for vote in self.get_votes():
            order = vote.get_order()
            if order.index(str(a.id)) < order.index(str(b.id)):
                count += 1
        return count
