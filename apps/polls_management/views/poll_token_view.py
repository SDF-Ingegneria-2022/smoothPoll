
from typing import List
from django.http import Http404, HttpRequest
from django.shortcuts import render
from django.urls import reverse
from sesame.utils import get_query_string

from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.services.poll_service import PollService
from django.contrib.auth.models import User

def poll_token(request: HttpRequest, poll_id: int):
    """View used to create specific poll tokens in details page."""

    token_number: int = int(request.POST.get('tokens'))

    # TODO: get the site home url instead
    link: str = "http://127.0.0.1:8000" + reverse('apps.votes_results:vote', 
            args=(poll_id,))
    
    links: List[str] = []
    templink: str = []

    # creation of a token link for as many times as dictated
    for x in range(token_number):
        phantomuser: User = User.objects.create_user(username="user"+str(x))
        templink = link
        templink += get_query_string(user=phantomuser)
        print(templink)
        
        links.append(templink)

    try:
        # Retrieve poll
        poll: PollModel = PollService.get_poll_by_id(poll_id)
    except Exception:
        raise Http404(f"Poll with id {poll_id} not found.")
    
    # Render details page with tokens list
    return render(request, 'votes_results/poll_details.html', {'poll': poll, 'token_links': links})
