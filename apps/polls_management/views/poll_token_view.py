
from typing import List
from django.http import Http404, HttpRequest, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.services.poll_service import PollService
from apps.polls_management.services.poll_token_service import PollTokenService

def poll_token(request: HttpRequest, poll_id: int):
    """View used to create specific poll tokens in details page."""

    try:
        # Retrieve poll
        poll: PollModel = PollService.get_poll_by_id(poll_id)
    except Exception:
        raise Http404(f"Poll with id {poll_id} not found.")

    if request.POST.get('tokens').isnumeric():
        token_number: int = int(request.POST.get('tokens'))
        #TODO: handle token number error to show in the page
        if token_number > 20:
            return HttpResponseRedirect(reverse('apps.polls_management:poll_details', args=(poll_id,)))
    else:
        return HttpResponseRedirect(reverse('apps.polls_management:poll_details', args=(poll_id,)))

    # TODO: get the site home url instead
    link: str = "http://127.0.0.1:8000" + reverse('apps.votes_results:vote', 
            args=(poll_id,))
    
    links: List[str] = PollTokenService.create_tokens(link, token_number, poll)
    
    # Render details page with tokens list
    return HttpResponseRedirect(reverse('apps.polls_management:poll_details', args=(poll_id,),))
    # return render(request, 'votes_results/poll_details.html', {'poll': poll, 'token_links': links})
