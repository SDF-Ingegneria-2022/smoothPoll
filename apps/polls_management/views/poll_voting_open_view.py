from django.shortcuts import render
from django.utils import timezone
from django.http import Http404, HttpRequest, HttpResponseRedirect
from django.urls import reverse
from apps.polls_management.classes.poll_form import PollForm
from apps.polls_management.exceptions.poll_cannot_be_opened_exception import PollCannotBeOpenedException
from apps.polls_management.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
from apps.polls_management.exceptions.poll_is_open_exception import PollIsOpenException
from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.services.poll_service import PollService
from apps.polls_management.views.poll_form_htmx_views import SESSION_ERROR, SESSION_FORMDATA, SESSION_OPTIONS, SESSION_POLL_ID, SESSION_IS_EDIT, clean_session
from allauth.account.decorators import login_required
from django.views.decorators.http import require_http_methods

@login_required
@require_http_methods(["POST"])
def open_poll_by_id(request: HttpRequest, poll_id: int):
    """Open poll voting now. If the poll is already open, redirect to all polls page. 
        If poll has not valid open/close time, redirect to create form.

    Args:
        request (HttpRequest): Request object.
        poll_id (int): The poll id.

    Raises:
        PollDoesNotExistException: If the poll not exist.
        PollIsOpenException: If the poll is open.
        PollCannotBeOpenedException: If the poll open/close time is not valid.
        
    Returns:
        HttpResponseRedirect: Reload the all polls page.
        HttpResponseRedirect: Redirect to create form.
    """

    try:
        # Retrieve poll
        poll: PollModel = PollService.get_poll_by_id(poll_id)
    except PollDoesNotExistException:
        raise Http404(f"Poll with id {poll_id} not found.")

    if (not request.user == poll.author):
        return render(request, 'global/not-author.html')
    
    try:
        PollService.open_poll(poll_id)
    except PollIsOpenException:
        return HttpResponseRedirect("%s?page=last&per_page=10" % reverse('apps.polls_management:all_user_polls'))
    except PollCannotBeOpenedException:
        # Redirect to modify form in order to set a valid open/close time
        form = PollForm({
            "name": poll.name, 
            "question": poll.question, 
            "poll_type": poll.poll_type, 
            "open_datetime": timezone.now(),
            "close_datetime": poll.close_datetime,
            "votable_mj": poll.votable_mj,  
        }, instance=poll)

        options: dict = {}
        i: int = 1
        for o in poll.options():
            options[str(i)] = o.value
            i += 1
        
        clean_session(request)
        # Set session data
        request.session[SESSION_IS_EDIT] = True
        request.session[SESSION_FORMDATA] = form.data
        request.session[SESSION_POLL_ID] = poll.id
        request.session[SESSION_OPTIONS] = options
        request.session[SESSION_ERROR] = "Per aprire al voto, inserisci una data di chiusura."

        # Redirect to form edit
        return HttpResponseRedirect(reverse('apps.polls_management:poll_form'))   

   