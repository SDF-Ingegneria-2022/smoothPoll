from django.utils import timezone
from django.http import Http404, HttpRequest, HttpResponseRedirect
from django.urls import reverse
from apps.polls_management.classes.poll_form import PollForm
from apps.polls_management.exceptions.poll_cannot_be_opened_exception import PollCannotBeOpenedException
from apps.polls_management.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
from apps.polls_management.exceptions.poll_is_open_exception import PollIsOpenException
from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.services.poll_service import PollService
from apps.polls_management.views.poll_form_htmx_views import SESSION_ERROR, SESSION_FORMDATA, SESSION_OPTIONS, SESSION_POLL_ID, clean_session


def poll_delete(request: HttpRequest, poll_id: int):
    """View method that deletes a poll

    Args:
        request (HttpRequest): Request object.
        poll_id (int): The poll id.

    Raises:
        PollDoesNotExistException: If the poll not exist.
        PollIsOpenException: If the poll is open.
        
    Returns:
        HttpResponseRedirect: Reload the all polls page.
    """

    # the POST method is used because the operation is going to potentially modify the database
    if request.method == "POST":
        try:
            # Retrieve poll
            poll: PollModel = PollService.get_poll_by_id(poll_id)
        except PollDoesNotExistException:
            raise Http404(f"Poll with id {poll_id} not found.")

        # If the delete poll service fails an error session variabile is setted to True
        # otherwise a success variable is setted to True and then reloaded the all_polls page in both cases
        try:
            PollService.delete_poll(str(poll_id))
        except PollIsOpenException:
            request.session['delete_error'] = True
            return HttpResponseRedirect("%s?page=last&per_page=10" % reverse('apps.polls_management:all_polls'))

        request.session['delete_success'] = True

        return HttpResponseRedirect("%s?page=last&per_page=10" % reverse('apps.polls_management:all_polls'))

def open_poll_by_id(request: HttpRequest, poll_id: int):
    """View method that opens a poll

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

    # the POST method is used because the operation is going to potentially modify the database
    if request.method == "POST":
        try:
            # Retrieve poll
            poll: PollModel = PollService.get_poll_by_id(poll_id)
        except PollDoesNotExistException:
            raise Http404(f"Poll with id {poll_id} not found.")

        try:
            PollService.open_poll(poll_id)
        except PollIsOpenException:
            return HttpResponseRedirect("%s?page=last&per_page=10" % reverse('apps.polls_management:all_polls'))
        except PollCannotBeOpenedException:
            form = PollForm({
                "name": poll.name, 
                "question": poll.question, 
                "poll_type": poll.poll_type, 
                "open_datetime": timezone.now(),
                "close_datetime": poll.close_datetime,  
            }, instance=poll)

            options: dict = {}
            i: int = 1
            for o in poll.options():
                options[str(i)] = o.value
                i += 1

            request.session[SESSION_FORMDATA] = form.data
            request.session[SESSION_POLL_ID] = poll.id
            request.session[SESSION_OPTIONS] = options

            request.session[SESSION_ERROR] = "Per aprire adesso il sondaggio inserisci la data di chiusura del sondaggio."

            # redirect to form to permit edit
            return HttpResponseRedirect(reverse('apps.polls_management:poll_form'))   

    return HttpResponseRedirect("%s?page=last&per_page=10" % reverse('apps.polls_management:all_polls'))