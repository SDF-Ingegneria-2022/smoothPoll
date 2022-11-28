from typing import List
from django.core.exceptions import ObjectDoesNotExist
from polls.exceptions.majority_number_of_ratings_not_valid import MajorityNumberOfRatingsNotValid
from polls.classes.majority_poll_result import MajorityPollResult
from polls.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
from polls.exceptions.poll_option_rating_unvalid_exception import PollOptionRatingUnvalidException
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
            rating_options: List of dictionaries of ratings assigned to an option [{'poll_choice_id': ..., 'rating_choosen': ...}, ...].
        Raises:
            PollDoesNotExistException: execption raised when the poll selected is not present in the database
            PollOptionRatingUnvalidException: exception raised when there are no rating choices in the options (None)
            MajorityNumberOfRatingsNotValid: exception raised when the rating number is not between 1 and 5
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

        # create majority vote object
        vote: MajorityVoteModel = MajorityVoteModel()
        vote.poll = poll_id
        vote.save()

        for num_ratings in rating_options:
            for rating_key, rating_value in num_ratings.items():
                temp_majority_option: MajorityOptionModel = MajorityOptionModel()
                temp_majority_option.poll_option = rating_key
                temp_majority_option.rating = rating_value
                temp_majority_option.poll_vote = vote.id  #Not sure about this
                temp_majority_option.save()
        
        return vote

    @staticmethod
    def calculate_result(poll_id: str) -> List[tuple(int)]:
        """
        Calculate result of a majority poll.
        """

        try:
            poll: PollModel = PollModel.objects.get(id=poll_id)
        except ObjectDoesNotExist:
            raise PollDoesNotExistException(f"Poll with id={poll_id} does not exist")

        poll_op: PollOptionModel = PollOptionModel.objects.filter(poll_fk=poll.id)
        result: MajorityPollResult = MajorityPollResult(poll, poll_op)

        median: int = result.majority_median()

        majority_vote_result_unsorted: list[tuple(int)] = []

        for majority_option in result.poll_options:
            majority_vote_result_unsorted.append(result.majority_count(majority_option, median))

        majority_vote_result = result.print_result(majority_vote_result_unsorted)

        return majority_vote_result

# to remake in a better way the calculate_result method