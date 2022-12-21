from django.http import Http404, HttpRequest, HttpResponseRedirect
from django.urls import reverse
from polls.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
from polls.exceptions.poll_has_been_voted_exception import PollHasBeenVotedException
from polls.models.poll_model import PollModel
from polls.services.poll_service import PollService

def poll_delete(request: HttpRequest, poll_id: int):
    """View method that deletes a poll
        Args:
        request (HttpRequest): Request object.
        poll_id (int): The poll id.
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
        except PollHasBeenVotedException:
            request.session['delete_error'] = True
            return HttpResponseRedirect("%s?page=last&per_page=10" % reverse('polls:all_polls'))

        request.session['delete_success'] = True

        return HttpResponseRedirect("%s?page=last&per_page=10" % reverse('polls:all_polls'))