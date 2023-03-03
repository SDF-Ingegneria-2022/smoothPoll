from typing import List
from django.core.exceptions import ObjectDoesNotExist
from apps.polls_management.classes.majority_poll_result_data import MajorityPollResultData
from apps.polls_management.exceptions.majority_number_of_ratings_not_valid import MajorityNumberOfRatingsNotValid
from apps.polls_management.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
from apps.polls_management.exceptions.poll_option_rating_unvalid_exception import PollOptionRatingUnvalidException
from apps.polls_management.exceptions.vote_does_not_exixt_exception import VoteDoesNotExistException
from apps.polls_management.models.majority_judgment_model import MajorityJudgmentModel
from apps.polls_management.models.majority_vote_model import MajorityVoteModel
from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.models.poll_option_model import PollOptionModel


class MajorityJudjmentVoteService:
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
        """Calculate result of a majority poll.
        
        Args:
            poll_id: The id of the poll.
        
        Raises:
            PollDoesNotExistException: If the poll does not exist.
            PollNotYetVodedException: If the poll didn't received votes.
        
        Returns: 
            List[MajorityPollResultData]: List of calculated result for each option.
        """

        try:
            poll: PollModel = PollModel.objects.get(id=poll_id)
        except ObjectDoesNotExist:
            raise PollDoesNotExistException(f"Poll with id={poll_id} does not exist")

        majority_vote_result_unsorted: List[MajorityPollResultData] = []

        all_options: PollOptionModel = PollOptionModel.objects.filter(poll_fk=poll)
        
        # calculate triplet <#worst votes, median(sign), #best votes> foreach option
        for option in all_options:

            option_result = MajorityPollResultData(option)
            majority_vote_result_unsorted.append(option_result)

        # sort result (descendant)
        majority_vote_result_unsorted.sort(reverse=True)

        return majority_vote_result_unsorted

    @staticmethod
    def get_vote_by_id(vote_id: str) -> MajorityVoteModel:
        """
        Retrieve a vote by its ID 
        (temporary method! In future we will wanna use <poll_id, user_id>)
        Args:
            vote_id: id of the vote object you want to retrieve
        Raises:
            VoteDoesNotExistException: if vote does not exists
        """

        try:
            return MajorityVoteModel.objects.get(id=vote_id)
        except ObjectDoesNotExist:
            raise VoteDoesNotExistException()