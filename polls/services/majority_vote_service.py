import math
from typing import List
from django.core.exceptions import ObjectDoesNotExist
from polls.classes.majority_poll_result_data import MajorityPollResultData
from polls.exceptions.majority_number_of_ratings_not_valid import MajorityNumberOfRatingsNotValid
from polls.classes.majority_poll_result import MajorityPollResult
from polls.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
from polls.exceptions.poll_option_rating_unvalid_exception import PollOptionRatingUnvalidException
from polls.models.majority_judgment_model import MajorityJudgmentModel
from polls.models.majority_vote_model import MajorityVoteModel
from polls.models.poll_model import PollModel
from polls.models.poll_option_model import PollOptionModel


class MajorityVoteService:
    """Class that handles vote procedures for the majority vote case"""

    @staticmethod
    def perform_vote(rating_options: List[dict], poll_id: str) -> MajorityVoteModel:
        """
        Perform a vote on a majority vote poll
        Args:
            poll_id: the id of the poll.
            rating_options: List of dictionaries of ratings assigned to an option [{'poll_choice_id': ..., 'rating': ...}, ...].
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

        num_poll_options: int = PollOptionModel.objects.filter(poll_fk=poll_id).count()
        if num_poll_options != len(rating_options):
            raise PollOptionRatingUnvalidException(f"Error: the poll option doesn't have a rating assigned")

        # check if rating assigned is a number from 1 to 5
        for num_ratings in rating_options:
            rating_value = num_ratings.get('rating')
            if rating_value < 1 or rating_value > 5:
                raise MajorityNumberOfRatingsNotValid(f"Error: the poll option has an invalid rating assigned")

        # todo: add a check if user alredy voted this

        # create majority vote object
        vote: MajorityVoteModel = MajorityVoteModel()
        vote.poll = poll
        vote.save()

        for num_ratings in rating_options:
            rating_key = num_ratings.get('poll_choice_id')
            rating_value = num_ratings.get('rating')

            temp_majority_option: MajorityJudgmentModel = MajorityJudgmentModel()
            temp_majority_option.poll_option = PollOptionModel.objects.filter(poll_fk=poll_id).get(id=rating_key)
            temp_majority_option.rating = rating_value
            temp_majority_option.majority_poll_vote = vote
            temp_majority_option.save()
        
        return vote

    @staticmethod
    def calculate_result(poll_id: str) -> List[MajorityPollResultData]:
        """
        Calculate result of a majority poll.
        """

        try:
            poll: PollModel = PollModel.objects.get(id=poll_id)
        except ObjectDoesNotExist:
            raise PollDoesNotExistException(f"Poll with id={poll_id} does not exist")

        result: MajorityPollResult = MajorityPollResult(poll)

        #median: int = result.majority_median(num)

        median: int = int(3)

        majority_vote_result_unsorted: List[MajorityPollResultData] = []

        all_options: PollOptionModel = PollOptionModel.objects.filter(poll_fk=poll)
        
        # calculate triplet <#worst votes, median(sign), #best votes> foreach option
        for option in all_options:

            # retrieve votes (ordered by rating)
            option_votes = MajorityJudgmentModel.objects \
                .filter(poll_option=option.id) \
                .order_by('rating')

            option_result = MajorityPollResultData()

            # calculate median (or worse of two)
            option_result.median = option_votes[math.floor(option_votes.count()/2)].rating

            # retrieve number of (strictly) greater and smaller votes
            option_result.good_votes: int = option_votes.filter(rating__gt=option_result.median).count()
            option_result.bad_votes: int = option_votes.filter(rating__lt=option_result.median).count()
            
            # set sign: 
            # if good > bad         --> +
            # else if good <= bad   --> -
            option_result.positive_grade = (option_result.good_votes > option_result.bad_votes)

        majority_vote_result = result.vote_result(majority_vote_result_unsorted)

        return majority_vote_result

# to remake in a better way the calculate_result method