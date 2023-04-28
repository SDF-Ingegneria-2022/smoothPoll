from django.http import Http404, HttpResponseRedirect, HttpRequest
from django.urls import reverse
from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.services.poll_service import PollService



def PollCloseView(request:HttpRequest, poll_id):

    try:
        # Retrieve poll
        poll: PollModel = PollService.get_poll_by_id(poll_id)
    except Exception:
        raise Http404(f"Poll with id {poll_id} not found.")
    if poll.is_open:
        PollService.close_poll(poll_id)
    
    return HttpResponseRedirect(reverse('apps.polls_management:poll_details', args=(poll_id,)))