from django.shortcuts import render
from django.http import Http404, HttpRequest, HttpResponseRedirect
from django.urls import reverse
from polls.models.poll_model import PollModel
from polls.services.poll_service import PollService

def poll_delete(request: HttpRequest, poll_id: int):
    """View method that deletes a poll"""

    try:
        # Retrieve poll
        poll: PollModel = PollService.get_poll_by_id(poll_id)
    except Exception:
        raise Http404(f"Poll with id {poll_id} not found.")

    # poll_delete_service(poll_id)

    # return HttpResponseRedirect(reverse('polls:poll_delete', args=(poll_id,)))

    return render(  request, 
                    'polls/all_polls.html', 
                    {
                    'delete_success': True
                    }
                )