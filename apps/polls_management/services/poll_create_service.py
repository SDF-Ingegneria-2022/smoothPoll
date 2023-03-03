from typing import List
from apps.polls_management.exceptions.poll_not_valid_creation_exception import *
from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.models.poll_option_model import PollOptionModel
from apps.polls_management.classes.poll_form_utils.poll_form import PollForm


class PollCreateService:
    """
    Services related to CRUD operation on Polls 
    """

    @staticmethod
    def create_or_edit_poll(poll_form: PollForm, options: List[str], user) -> PollModel:
        """Create a new poll starting from a PollForm object (or
        apply the edits on the existing object)
         
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
            raise PollMainDataNotValidException(f"Some data of passed poll_form is not valid. See errors:\n{poll_form.errors}")

        # validate options
        valid_options = list()
        for o in options:
            if o.strip() != "":
                valid_options.append(o)

        # ensuring is passed at least a certain number of options
        if len(valid_options) < poll_form.get_min_options():
            raise TooFewOptionsException(f"{poll_form.data.get('poll_type')} poll " +
                f"(votable_mj={poll_form.data.get('votable_mj')}) needs at least " +
                f"{poll_form.get_min_options()} options, {len(valid_options)} has given")

        # all polls can have at most 10 options
        if len(valid_options) > 10:
            raise TooManyOptionsException(f"A poll accepts at most 10 options, {len(valid_options)} has given")
        
        # create poll object from form
        poll = poll_form.save(commit=False)
        poll.author = user
        poll.save()


        # check if there are already options in the poll object
        # and delete them (edit case)
        if poll.options():
            for previous_option in poll.options():
                previous_option.delete()

        # create option objects
        for o_str in valid_options:
            option = PollOptionModel(value=o_str)
            option.poll_fk = poll
            option.save()
        
        return poll



