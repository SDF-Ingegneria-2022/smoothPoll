from polls.classes.vote_builder import VoteBuilder
from polls.models.poll_model import PollModel
from polls.models.poll_option_model import PollOptionModel
from polls.models.vote_model import VoteModel
from polls.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
from polls.exceptions.poll_option_unvalid_exception import PollOptionUnvalidException
from django.core.exceptions import ObjectDoesNotExist
from polls.classes.poll_result import PollResult

class VoteService: 
    """
    Handle vote procedures 
    """

    @staticmethod
    def perform_vote(poll_id: str, poll_choice_id: str) -> VoteModel:
        """
        Perform a vote on a survey.
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
    def calculate_result(poll_id: str) -> PollResult:
        """
        Calculate result of a poll.
        """

        try:
            poll: PollModel = PollModel.objects.get(id=poll_id)
        except ObjectDoesNotExist:
            raise PollDoesNotExistException(f"Poll with id={poll_id} does not exist")

        return PollResult(poll)

