from django.shortcuts import render
from django.utils import timezone
from django.http import Http404, HttpRequest, HttpResponseRedirect
from django.urls import reverse
from apps.polls_management.exceptions.poll_cannot_be_opened_exception import PollCannotBeOpenedException
from apps.polls_management.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
from apps.polls_management.exceptions.poll_is_open_exception import PollIsOpenException
from apps.polls_management.models.poll_model import OPEN_DATETIME, PollModel
from apps.polls_management.services.poll_service import PollService
from apps.polls_management.classes.poll_form_utils.poll_form_session import init_session_for_edit, clean_session
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

        clean_session(request)

        init_session_for_edit(request, poll, 
                              override_data={ OPEN_DATETIME: timezone.now(), }, 
                              error_message="Per aprire adesso la scelta, inserisci una data di chiusura."
                              )


        # Redirect to form edit
        return HttpResponseRedirect(reverse('apps.polls_management:poll_form'))   

   