from polls.exceptions.poll_not_valid_creation_exception import PollNotValidCreationException
from polls.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
from polls.models import PollModel
from polls.models.poll_option_model import PollOptionModel
from polls.classes.poll_form import PollForm


class PollCreateService:
    """
    Services related to CRUD operation on Polls 
    """

    @staticmethod
    def create_new_poll(poll_form: PollForm):
        """
        Create a new poll starting from a PollForm object. 
        New poll will be set as unvalid 
        """
        pass


