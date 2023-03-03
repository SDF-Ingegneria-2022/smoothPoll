from apps.votes_results.classes.vote_builder import VoteBuilder
from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.models.vote_model import VoteModel
from apps.polls_management.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
from apps.votes_results.exceptions.vote_does_not_exixt_exception import VoteDoesNotExistException
from django.core.exceptions import ObjectDoesNotExist
from apps.votes_results.classes.poll_result import PollResult

class SingleOptionVoteService: 
    """
    Handle vote procedures like:

    - perform a vote on a simple poll (one choice)
    - calculate results on a simple poll
    """

    @staticmethod
    def perform_vote(poll_id: str, poll_choice_id: str) -> VoteModel:
        """
        Perform a vote on a survey.
        Args:
            poll_id: id of poll you want to vote
            poll_choice_id: the voted option
        Raises: 
            PollDoesNotExistException: you tried to vote a not existent poll
            PollOptionUnvalidException: you tried to vote an unvalid option 
                (id doesn't exists or it doesn't belong to this poll)
        """

        vote_builder = VoteBuilder()

        vote_builder.set_poll(poll_id)
        vote_builder.set_voted_option(poll_choice_id)
        
        vote: VoteModel = vote_builder.perform_creation()
        vote.save()
        
        return vote

    @staticmethod
    def get_vote_by_id(vote_id: str) -> VoteModel:
        """
        Retrieve a vote by its ID 
        (temporary method! In future we will wanna use <poll_id, user_id>)
        Args:
            vote_id: id of the vote object you want to retrieve
        Raises:
            VoteDoesNotExistException: if vote does not exists
        """

        try:
            return VoteModel.objects.get(id=vote_id)
        except ObjectDoesNotExist:
            raise VoteDoesNotExistException()

    @staticmethod
    def calculate_result(poll_id: str) -> PollResult:
        """
        Calculate result of a poll.
        Args:
            poll_id: id of poll you want to calculate results
        Raises:
            PollDoesNotExistException: you tried to calculate results on a non-existent poll
        """

        try:
            poll: PollModel = PollModel.objects.get(id=poll_id)
        except ObjectDoesNotExist:
            raise PollDoesNotExistException(f"Poll with id={poll_id} does not exist")

        return PollResult(poll)

