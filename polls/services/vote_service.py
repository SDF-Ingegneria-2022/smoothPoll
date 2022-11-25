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
        """

        # vote = VoteFactory.create_vote(poll_id, poll_choice_id)

        # check if poll exists
        try:
            poll: PollModel = PollModel.objects.get(id=poll_id)
            # todo: add here "is open" filter
        except ObjectDoesNotExist:
            raise PollDoesNotExistException(f"Error: Poll with id={poll_id} does not exist")

        # check if option exists
        try:
            poll_choice: PollOptionModel = PollOptionModel.objects.filter(poll_fk=poll.id).get(id=poll_choice_id)
        except ObjectDoesNotExist:
            raise PollOptionUnvalidException(f"Error: PollOption with id={poll_choice_id} does " +
            f"not exist or it is not related to Poll with id={poll_id}")

        # todo: add a check if user alredy voted this

        # create vote object
        vote: VoteModel = VoteModel()
        vote.poll_option = poll_choice
        
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

