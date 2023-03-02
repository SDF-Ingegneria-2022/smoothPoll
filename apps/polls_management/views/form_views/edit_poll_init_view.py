from apps.polls_management.classes.poll_form_utils.poll_form import PollForm
from apps.polls_management.classes.poll_form_utils.poll_form_session import SESSION_FORMDATA, SESSION_IS_EDIT, SESSION_OPTIONS, SESSION_POLL_ID, clean_session
from apps.polls_management.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.exceptions.poll_not_valid_creation_exception import *
from apps.polls_management.services.poll_service import PollService
from django.http import HttpRequest, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from allauth.account.decorators import login_required

@login_required
def edit_poll_init_view(request: HttpRequest, poll_id: int):
    """View to inizialize form for new poll creation"""

    # clean session from eventual mess
    clean_session(request)
    
    try:
        # Retrieve poll
        poll: PollModel = PollService.get_poll_by_id(poll_id)
    except PollDoesNotExistException:
        raise Http404(f"Poll with id {poll_id} not found.")
    
    if (not request.user == poll.author):
        return render(request, 'global/not-author.html')

    # Check if poll is open and can be edit
    if poll.is_open() or poll.is_closed():
        request.session['cannot_edit'] = True
        return HttpResponseRedirect("%s?page=last&per_page=10" % reverse('apps.polls_management:all_user_polls'))

    # init form with poll instance that should be modified 
    form = PollForm({
        "name": poll.name, 
        "question": poll.question, 
        "poll_type": poll.poll_type, 
        "open_datetime": poll.open_datetime,
        "close_datetime": poll.close_datetime,  
        "autor": poll.author,
        "votable_mj": poll.votable_mj, 
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

    # redirect to form to permit edit
    return HttpResponseRedirect(reverse('apps.polls_management:poll_form'))   

