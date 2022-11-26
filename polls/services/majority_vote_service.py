from typing import List
from django.core.exceptions import ObjectDoesNotExist
from polls.exceptions.majority_number_of_ratings_not_valid import MajorityNumberOfRatingsNotValid
#from polls.classes.majority_poll_result import MajorityPollResult
from polls.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
from polls.exceptions.poll_option_rating_unvalid_exception import PollOptionRatingUnvalidException
from polls.exceptions.poll_option_unvalid_exception import PollOptionUnvalidException
from polls.models.majority_option_model import MajorityOptionModel
from polls.models.majority_vote_model import MajorityVoteModel
from polls.models.poll_model import PollModel
from polls.models.poll_option_model import PollOptionModel


class MajorityVoteService:
    """Class that handles vote procedures for the majority vote case"""

    @staticmethod
    def perform_vote(poll_id: str, rating_options: List[dict]) -> MajorityVoteModel:
        """
        Perform a vote on a majority vote poll
        Args:
            poll_id: the id of the poll.
            rating_options: List of ratings assigned to an option [{'poll_choice_id': ..., 'rating_choosen': ...}, ...].
        Raises:
            PollNotValidCreationException: Is raised when the poll is not valid. When the input params not meet the requirements.
        Returns:
            MajorityVoteModel: the majority vote model created.
        """

        # check if poll exists
        try:
            poll: PollModel = PollModel.objects.get(id=poll_id)
            # todo: add here "is open" filter
        except ObjectDoesNotExist:
            raise PollDoesNotExistException(f"Error: Poll with id={poll_id} does not exist")

        # check if every option has a value assigned
        for num_ratings in rating_options:
            for rating in num_ratings.values():
                if rating is None:
                    raise PollOptionRatingUnvalidException(f"Error: the poll option doesn't have a rating assigned")

        # check if rating assigned is a number from 1 to 5
        for num_ratings in rating_options:
            for rating in num_ratings.values():
                if rating < 1 or rating > 5:
                    raise MajorityNumberOfRatingsNotValid(f"Error: the poll option has an invalid rating assigned")

        # todo: add a check if user alredy voted this

        # create vote object
        vote: MajorityVoteModel = MajorityVoteModel()
        vote.poll = poll_id
        vote.save()

        for num_ratings in rating_options:
            for rating_key, rating_value in num_ratings.items():
                temp_majority_option: MajorityOptionModel = MajorityOptionModel
                temp_majority_option.poll_option = rating_key
                temp_majority_option.rating = rating_value
                temp_majority_option.poll_rating = vote.id  #Not sure about this
                temp_majority_option.save()
        
        return vote

    #@staticmethod
    #def calculate_result(poll_id: str) -> MajorityPollResult:
        """
        Calculate result of a majority poll.
        """

        try:
            poll: PollModel = PollModel.objects.get(id=poll_id)
        except ObjectDoesNotExist:
            raise PollDoesNotExistException(f"Poll with id={poll_id} does not exist")

        return MajorityPollResult(poll)