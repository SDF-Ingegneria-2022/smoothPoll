from typing import List
from django.http import Http404, HttpRequest
from django.shortcuts import render

from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.services.poll_service import PollService
from apps.polls_management.services.poll_token_service import PollTokenService


def poll_details(request: HttpRequest, poll_id: int):
    """Render the details page for a poll"""
    try:
        # Retrieve poll
        poll: PollModel = PollService.get_poll_by_id(poll_id)
    except Exception:
        raise Http404(f"Poll with id {poll_id} not found.")
    
    if poll.is_votable_token():
        token_links = PollTokenService.available_token_list(poll)
        invalid_tokens = PollTokenService.unavailable_token_list(poll)
        return render(request, 'votes_results/poll_details.html', {'poll': poll, 'token_list': token_links, 'invalid_tokens': invalid_tokens})
    else:
        # Render vote form (with eventual error message)
        return render(request, 'votes_results/poll_details.html', {'poll': poll})