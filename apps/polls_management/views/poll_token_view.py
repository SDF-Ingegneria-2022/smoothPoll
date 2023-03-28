
from typing import List
from django.http import Http404, HttpRequest
from django.shortcuts import render
from django.urls import reverse
from sesame.utils import get_query_string

from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.services.poll_service import PollService


def poll_token(request: HttpRequest, poll_id: int, token_number: int):
    """View used to create specific poll tokens in details page."""

    link: str = reverse('apps.votes_results:vote', 
            args=(poll_id,))
    
    links: List = []

    for x in range(token_number):
        link += get_query_string(user=request.user, scope=f"poll:{poll_id}")
        links.append(link)

    try:
        # Retrieve poll
        poll: PollModel = PollService.get_poll_by_id(poll_id)
    except Exception:
        raise Http404(f"Poll with id {poll_id} not found.")
    
    # Render vote form (with eventual error message)
    return render(request, 'votes_results/poll_details.html', {'poll': poll, 'link': links})
