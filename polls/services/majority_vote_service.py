from django.core.exceptions import ObjectDoesNotExist
from polls.classes.majority_poll_result import MajorityPollResult
from polls.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
from polls.exceptions.poll_option_rating_unvalid_exception import PollOptionRatingUnvalidException
from polls.exceptions.poll_option_unvalid_exception import PollOptionUnvalidException
from polls.models.majority_vote_model import MajorityVoteModel
from polls.models.poll_model import PollModel
from polls.models.poll_option_model import PollOptionModel


class MajorityVoteService:
    """Class that handles vote procedures for the majority vote case"""

    @staticmethod
    def perform_vote(poll_id: str, poll_choice_id: str, majority_rating_choice_id: str) -> MajorityVoteModel:
        """
        Perform a vote on a majority vote survey
        """

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

        # check if rating choice exists
        try:
            majority_rating_choice: MajorityVoteModel = MajorityVoteModel.objects.filter(poll_fk=poll_id).filter(poll_option=poll_choice_id).get(id=majority_rating_choice_id)
        except ObjectDoesNotExist:
            raise PollOptionRatingUnvalidException(f"Error: PollOptionRating with id={majority_rating_choice_id} does " +
            f"not exist or it is not related to PollOption with id={poll_choice_id} or the Poll with id={poll_id}")

        # todo: add a check if user alredy voted this

        # create vote object
        vote: MajorityVoteModel = MajorityVoteModel()
        vote.rating_option = majority_rating_choice
        
        vote.save()
        
        return vote

    @staticmethod
    def calculate_result(poll_id: str) -> MajorityPollResult:
        """
        Calculate result of a majority poll.
        """

        try:
            poll: PollModel = PollModel.objects.get(id=poll_id)
        except ObjectDoesNotExist:
            raise PollDoesNotExistException(f"Poll with id={poll_id} does not exist")

        return MajorityPollResult(poll)