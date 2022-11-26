from typing import List
from polls.exceptions.majority_number_of_ratings_not_valid import MajorityNumberOfRatingsNotValid
from polls.models.majority_option import MajorityOption
from polls.models.poll_option_model import PollOptionModel

class MajorityPollOptionService:
    """Service to handle majority poll option ratings"""

    @staticmethod
    def create(num_rating: int, poll_option_id: str) -> List[MajorityOption]:
        """Creates a new poll option.
        Args:
            rating: rating of the poll option
        Returns:
            MajorityOption: The created list of majority poll option ratings.
        """

        if num_rating < 3 or num_rating > 9:
            raise MajorityNumberOfRatingsNotValid("Number of ratings is not valid for creation")

        ratings: List[MajorityOption] = []
        rating_index: int(1)

        while rating_index <= num_rating:
            new_rating: MajorityOption = MajorityOption(rating=rating_index, poll_option=poll_option_id)
            new_rating.save()
            ratings.append(new_rating)
            rating_index += 1

        return ratings

    @staticmethod
    def get_by_poll_option_id(poll_option_id: str) -> PollOptionModel:
        """Get a poll option by its id.
        Args:
            id: Id of the option.
        Returns:
            PollOptionModel: Single poll option that satisfies the id.
        """
        poll_option: PollOptionModel = PollOptionModel.objects.get(id=poll_option_id)
        return  poll_option