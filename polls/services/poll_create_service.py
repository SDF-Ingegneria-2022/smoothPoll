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
        """Create a new poll starting from a PollForm object. 
        Args:
            poll_form: form containing data of object you wanna create.
            options: list of all options (as strings). 
                They must be at least 2 and at most 10.
        
        Raises:
            MissingNameOrQuestionExcetion: your form has not all required data.
            TooFewOptionsExcetion: you put in too few options for this type of poll.
            TooManyOptionsExcetion: you put in too many options for this type of poll.
                
        Returns:
            The initialized and saved PollModel object
        """

        # validate form
        if not poll_form.is_valid():
            raise NameOrQuestionNotValidException()

        # validate options
        valid_options = list()
        for o in options:
            if o.strip() != "":
                valid_options.append(o)

        if len(valid_options) < 2:
            raise TooFewOptionsException()

        if len(valid_options) > 10:
            raise TooManyOptionsException()
        
        # create poll object from form
        poll = poll_form.save()

        # create option objects
        for o_str in valid_options:
            option = PollOptionModel(value=o_str)
            option.poll_fk = poll
            option.save()

        return poll



