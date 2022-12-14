from typing import List
from polls.exceptions.poll_not_valid_creation_exception import *
from polls.models import PollModel
from polls.models.poll_option_model import PollOptionModel
from polls.classes.poll_form import PollForm


class PollCreateService:
    """
    Services related to CRUD operation on Polls 
    """

    @staticmethod
    def create_new_poll(poll_form: PollForm, options: List[str]) -> PollModel:
        """
        Create a new poll starting from a PollForm object. 
        Args:
            poll_form: form containing data of object you wanna create.
            options: list of all options (as strings). 
                They must be at least 2 and at most 10.
        Return:
            The initialized and saved PollModel object
        Raise:
            MissingNameOrQuestionExcetion: your form has not all required data.
            TooFewOptionsExcetion: you put in too few options for this type of poll.
            TooManyOptionsExcetion: you put in too many options for this type of poll.
        """

        if not poll_form.is_valid():
            raise NameOrQuestionNotValidException()
        
        poll = poll_form.save()

        for o_str in options:
            option = PollOptionModel(value=o_str)
            option.poll_fk = poll
            option.save()

        return poll



