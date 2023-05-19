from typing import List
from django.core.exceptions import ObjectDoesNotExist
from apps.polls_management.models.schulze_vote_model import SchulzeVoteModel
from apps.votes_results.classes.majority_poll_result_data import MajorityPollResultData
from apps.polls_management.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
from apps.votes_results.classes.schulze_results.schulze_results_adapter import SchulzeResultsAdapter
from apps.votes_results.exceptions.results_not_available_exception import ResultsNotAvailableException
from apps.votes_results.exceptions.vote_does_not_exixt_exception import VoteDoesNotExistException
from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.models.poll_option_model import PollOptionModel


class SchulzeMethodVoteService:
    """Class that handles vote procedures for the majority vote case"""

    @staticmethod
    def perform_vote(options_rated: List[str], poll_id: str) -> SchulzeVoteModel:
        """
        Perform a vote on a majority vote poll
        Args:
            poll_id: the id of the poll.
            options_rated: List of string of option id [12,14,13,15] 
        Raises:
            PollDoesNotExistException: execption raised when the poll selected is not present in the database
        Returns:
            SchulzeVoteModel: the schulze vote model created.
        """

        # check if poll exists
        try:
            poll: PollModel = PollModel.objects.get(id=poll_id)
        except ObjectDoesNotExist:
            raise PollDoesNotExistException(f"Error: Poll with id={poll_id} does not exist")


        # create schulze vote object
        vote: SchulzeVoteModel = SchulzeVoteModel()
        vote.poll = poll
        user_order :List = []
        for opt in options_rated:
            user_order.append(int(opt))
        vote.set_order(user_order)
        vote.save()
        
        return vote

    @staticmethod
    def calculate_result(poll: PollModel, user = None) -> SchulzeResultsAdapter:
        """
        Calculate result of a poll.
        Args:
            poll: the poll you want to calculate results
        Raises:
            PollDoesNotExistException: you tried to calculate results on a non-existent poll
            ResultsNotAvailableException: raised if you try to check results not visible
        """

        try:
            poll: PollModel = PollModel.objects.get(id=poll.id)
        except ObjectDoesNotExist:
            raise PollDoesNotExistException(f"Poll with id={poll.id} does not exist")
        
        # check if the results can be viewed
        if not poll.are_results_visible(user):
            raise ResultsNotAvailableException(f"Results of poll with id={poll.id} are not available")
        
        result: SchulzeResultsAdapter = SchulzeResultsAdapter(poll)
        result.calculate()

        return result

    @staticmethod
    def get_vote_by_id(vote_id: str) -> SchulzeVoteModel:
        """
        Retrieve a vote by its ID 
        (temporary method! In future we will wanna use <poll_id, user_id>)
        Args:
            vote_id: id of the vote object you want to retrieve
        Raises:
            VoteDoesNotExistException: if vote does not exists
        """

        try:
            return SchulzeVoteModel.objects.get(id=vote_id)
        except ObjectDoesNotExist:
            raise VoteDoesNotExistException()