
from typing import List
from django.http import Http404, HttpRequest, HttpResponseRedirect
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

    # check for errors in token generation form
    if request.POST.get('tokens').isnumeric():
        token_number: int = int(request.POST.get('tokens'))
        if token_number <=0:
            return HttpResponseRedirect(reverse('apps.polls_management:poll_details', args=(poll_id,)))
    else:
        return HttpResponseRedirect(reverse('apps.polls_management:poll_details', args=(poll_id,)))

    # creation of links with token embedded for the specified poll
    link: str = "http://" + request.get_host() + reverse('apps.votes_results:vote', 
            args=(poll_id,))
    
    links: List[str] = PollTokenService.create_tokens(link, token_number, poll)
    
    # Render details page with tokens list
    return HttpResponseRedirect(reverse('apps.polls_management:poll_details', args=(poll_id,),))
    # return render(request, 'votes_results/poll_details.html', {'poll': poll, 'token_links': links})

def delete_poll_token(request: HttpRequest, poll_id: int):
    """View used to delete all poll tokens and phantom users in details page."""

    # the POST method is used because the operation is going to potentially modify the database
    if request.method == "POST":
        try:
            # Retrieve poll
            poll: PollModel = PollService.get_poll_by_id(poll_id)
        except Exception:
            raise Http404(f"Poll with id {poll_id} not found.")
        
        PollTokenService.delete_tokens(poll)

        return HttpResponseRedirect(reverse('apps.polls_management:poll_details', args=(poll_id,)))