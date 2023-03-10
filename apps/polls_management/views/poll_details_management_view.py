from django.http import Http404, HttpRequest
from django.shortcuts import render

from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.services.poll_service import PollService


def poll_details(request: HttpRequest, poll_id: int):
    """Render the details page for a poll"""
    try:
        # Retrieve poll
        poll: PollModel = PollService.get_poll_by_id(poll_id)
    except Exception:
        raise Http404(f"Poll with id {poll_id} not found.")
    
    # Render vote form (with eventual error message)
    return render(request, 'votes_results/poll_details.html', {'poll': poll})