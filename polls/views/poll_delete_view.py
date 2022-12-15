from django.shortcuts import render
from django.http import Http404, HttpRequest, HttpResponseRedirect
from django.urls import reverse
from polls.models.poll_model import PollModel
from polls.services.poll_service import PollService

def poll_delete(request: HttpRequest, poll_id: int):
    """View method that deletes a poll"""

    if request.method == "POST":
        try:
            # Retrieve poll
            poll: PollModel = PollService.get_poll_by_id(poll_id)
        except Exception:
            raise Http404(f"Poll with id {poll_id} not found.")

        # try:
        #     poll_delete_service(poll_id)
        # except Exception:
        #     request.session['delete_error'] = True

        request.session['delete_success'] = True

        return HttpResponseRedirect("%s?page=last&per_page=10" % reverse('polls:all_polls'))