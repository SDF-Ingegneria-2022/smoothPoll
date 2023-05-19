from typing import List
from apps.polls_management.classes.schulze_algorithm import schulze
from apps.polls_management.models.poll_option_model import PollOptionModel
from apps.polls_management.models.schulze_vote_model import SchulzeVoteModel
from apps.votes_results.classes.schulze_results.i_schulze_results import ISchulzeResults
from django.core.exceptions import ObjectDoesNotExist
from apps.votes_results.exceptions.poll_not_yet_voted_exception import PollNotYetVodedException
from apps.votes_results.exceptions.vote_does_not_exixt_exception import VoteDoesNotExistException

class SchulzeResultsAdapter(ISchulzeResults):
    """Class used to manage data for a Schulze poll results"""
    
    schulze_votes: List[SchulzeVoteModel]
    """List containing all the votes for the specified schulze poll."""

    schulze_results: List[List[PollOptionModel]]
    """List containing all the results in the winning order."""

    schulze_str_options: List[str]
    """List containing all the options of the poll as list of string ids."""

    all_schulze_rankings: List[List[List[str]]]
    """List containing all the order rankings of the poll as list of string ids."""

    def get_votes(self) -> List[SchulzeVoteModel]:
        return self.schulze_votes
    
    def get_sorted_options(self) -> List[List[PollOptionModel]]:
        return self.schulze_results
    
    def calculate(self) -> None:

        self.set_votes()
        self.set_options()
        self.set_all_rankings()
        # now we have all the elements to calcluate the results with the algorithm
        self.set_schulze_results()

    def set_votes(self) -> None:
        
        try:
            self.schulze_votes = list(SchulzeVoteModel.objects.filter(poll=self.poll))
        except ObjectDoesNotExist:
            raise VoteDoesNotExistException(f"The vote model does not exist.")
        
        if len(self.schulze_votes) < 1:
            raise PollNotYetVodedException()

    def set_options(self) -> None:
        self.schulze_str_options = self.schulze_votes[0].get_order_as_ids()

    def set_all_rankings(self) -> None:

        all_rankings: List[List[List[str]]] = []
        for vote in self.schulze_votes:
            vote_list: List[List[str]] = [[i] for i in vote.get_order()]
            all_rankings.append(vote_list)

        self.all_schulze_rankings = all_rankings

    def set_schulze_results(self) -> None:

        # from the schulze algorithm, we need to "candidate names" and "ballots"
        # respectively 'schulze_str_options' and 'all_schulze_rankings'
        result: List[List[str]] = schulze.compute_schulze_ranking(self.schulze_str_options, self.all_schulze_rankings)
        
        rankings: List[List[PollOptionModel]] = []
        for id in result:
            same_rank_list: List[PollOptionModel] = []
            for same_rank in id:
                option: PollOptionModel = PollOptionModel.objects.get(id=int(same_rank))
                same_rank_list.append(option)
            rankings.append(same_rank_list)

        self.schulze_results = rankings



