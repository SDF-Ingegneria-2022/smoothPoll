from django.http import Http404, HttpRequest
from apps.polls_management.classes.poll_form_utils.poll_form import PollForm
from apps.polls_management.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
from apps.polls_management.exceptions.poll_not_valid_creation_exception import *
from apps.polls_management.services.poll_service import PollService
from apps.polls_management.models.poll_model import RANDOMIZE_OPTIONS, PollModel, NAME, \
                                                    QUESTION, POLL_TYPE, \
                                                    OPEN_DATETIME, CLOSE_DATETIME,\
                                                    PREDEFINITED, VOTABLE_MJ, AUTHOR,\
                                                    PRIVATE, SHORT_ID

# Session keys used to store form data 
# (or create/edit process data)

SESSION_FORMDATA = 'create-poll-form'
SESSION_POLL_ID = 'poll-instance'
SESSION_OPTIONS = 'create-poll-options'
SESSION_ERROR = 'create-poll-error'
SESSION_IS_EDIT = 'is-edit'


_ALL_SESSION_KEYS = [
    SESSION_FORMDATA, 
    SESSION_OPTIONS, 
    SESSION_ERROR, 
    SESSION_POLL_ID, 
    SESSION_IS_EDIT ]

# -------------------------------------------------
# Session util methods (methods to perform some
# operations on session during creation)

def clean_session(request: HttpRequest) -> None: 
    """Clean current session from form data"""

    # iterate all keys used to store form data
    # to delete each of them
    for key in _ALL_SESSION_KEYS:
        if request.session.get(key) is not None:
            del request.session[key]


def get_poll_form(request: HttpRequest) -> PollForm:
    """Factory method to get current form 
    from session (or from POST request)."""

    # build a form for creation (w most updated data)
    if request.session.get(SESSION_POLL_ID) is None:
        
        return PollForm(request.POST or request.session.get(SESSION_FORMDATA) or None)

    # build a form for editing an existing instance
    try:
        return PollForm(
            # fill form data w current most updated
            request.POST or request.session.get(SESSION_FORMDATA) or None, 

            # connect form to existing instance
            instance= PollService.get_poll_by_id(
                request.session.get(SESSION_POLL_ID))
        )
    except PollDoesNotExistException:
        raise Http404(f"Poll with id {request.session.get(SESSION_POLL_ID)} not found.")
    

def init_session_for_edit(request: HttpRequest, poll: PollModel, 
                          override_data: dict = {}, 
                          error_message: str = None) -> None:
    """Init session for edit. Run this method to prepare the 
    session for using the form to edit a poll.

    Args:
        request (HttpRequest): Request object.
        poll (PollModel): The poll you wanna edit.
        override_data (dict): Use this dict to override some params.
        error_message (str): Use this field to show user an initial error message.    
    """
    
    # init form with poll instance that should be modified 
    form = PollForm({
        NAME: override_data.get(NAME, poll.name), 
        QUESTION: override_data.get(QUESTION, poll.question), 
        POLL_TYPE: override_data.get(POLL_TYPE, poll.poll_type), 
        OPEN_DATETIME: override_data.get(OPEN_DATETIME, poll.open_datetime),
        CLOSE_DATETIME: override_data.get(CLOSE_DATETIME, poll.close_datetime),  
        AUTHOR: override_data.get(AUTHOR, poll.author),
        VOTABLE_MJ: override_data.get(VOTABLE_MJ, poll.votable_mj),
        PRIVATE: override_data.get(PRIVATE, poll.private), 
        SHORT_ID: override_data.get(SHORT_ID, poll.short_id), 
        RANDOMIZE_OPTIONS: override_data.get(RANDOMIZE_OPTIONS, poll.randomize_options)
    }, instance=poll)

    # init poll options with current ones
    options: dict = {}
    i: int = 1
    for o in poll.options():
        options[str(i)] = o.value
        i += 1

    # save everythingh in session, so form can be 
    # rendered with current data
    request.session[SESSION_FORMDATA] = form.data
    request.session[SESSION_POLL_ID] = poll.id
    request.session[SESSION_OPTIONS] = options
    request.session[SESSION_IS_EDIT] = True

    # write in session eventual error message
    if not error_message is None:
        request.session[SESSION_ERROR] = error_message

