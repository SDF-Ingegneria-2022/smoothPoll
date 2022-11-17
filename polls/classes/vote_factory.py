from polls.models.poll_model import PollModel
from polls.models.poll_option_model import PollOptionModel
from polls.models.vote_model import VoteModel

from django.core.exceptions import ObjectDoesNotExist

class VoteFactory(): 
    """
    A tool to perform a votation and ensure safety.
    """

    @staticmethod
    def create_vote(poll_id: str, poll_choice_id: str) -> PollModel: 
        """
        Create a vote (ensuring all properties)
        """
        
        # check if poll exists
        try:
            poll: PollModel = PollModel.objects.get(id=poll_id)
            # todo: add here "is open" filter
        except ObjectDoesNotExist:
            from polls.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
            raise PollDoesNotExistException(f"Error: Poll with id={poll_id} does not exist")

        # check if option exists
        try:
            poll_choice: PollOptionModel = PollOptionModel.objects.filter(poll_fk=poll.id).get(id=poll_choice_id)
        except ObjectDoesNotExist:
            from polls.exceptions.poll_option_unvalid_exception import PollOptionUnvalidException
            raise PollOptionUnvalidException(f"Error: PollOption with id={poll_choice_id} does " +
            f"not exist or it is not related to Poll with id={poll_id}")

        # todo: add a check if user alredy voted this

        # create vote object
        vote: VoteModel = VoteModel()
        vote.poll_option = poll_choice

        return vote

    

        




