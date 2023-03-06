from django.http import Http404, HttpRequest
from apps.polls_management.classes.poll_form_utils.poll_form import PollForm
from apps.polls_management.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
from apps.polls_management.exceptions.poll_not_valid_creation_exception import *
from apps.polls_management.services.poll_service import PollService

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