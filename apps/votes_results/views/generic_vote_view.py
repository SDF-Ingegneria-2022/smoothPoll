from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.services.poll_service import PollService
from apps.polls_management.services.poll_token_service import PollTokenService
from apps.polls_management.models.poll_token import PollTokens
from sesame.decorators import authenticate
from sesame.utils import get_user, get_token
from django.contrib.auth import logout

@authenticate(required=False)
def generic_vote_view(request, poll_id: int):
    """Redirect to poll's main vote method"""

    try:
        # Retrieve poll
        poll: PollModel = PollService.get_poll_by_id(poll_id)
    except Exception:
        raise Http404(f"Poll with id {poll_id} not found.")
    
    # add control if poll is votable only with tokens
    if poll.votable_token:
        try:
            token_poll_data = PollTokenService.get_poll_token_by_user(request.user)
        except Exception:
            return render(request, 'polls_management/token_poll_redirect.html', {'poll': poll})
        
        # token validation controls
        if PollTokenService.is_single_option_token_used(token_poll_data) and not poll.votable_mj:
            logout(request)
            return render(request, 'polls_management/token_poll_redirect.html', {'poll': poll})
        elif PollTokenService.is_single_option_token_used(token_poll_data) and poll.votable_mj:
            return HttpResponseRedirect(
                reverse('apps.votes_results:majority_judgment_vote', args=(poll_id,)))
        elif PollTokenService.is_majority_token_used(token_poll_data):
            logout(request)
            return render(request, 'polls_management/token_poll_redirect.html', {'poll': poll})
        
        # pass the token to specific poll type view for vote
        request.session['token_used'] = token_poll_data

    # redirect to proper vote method
    if poll.poll_type == PollModel.PollType.MAJORITY_JUDJMENT:
        return HttpResponseRedirect(
            reverse('apps.votes_results:majority_judgment_vote', args=(poll_id,)))
    else:
        return HttpResponseRedirect(reverse(
            'apps.votes_results:single_option_vote', 
            args=(poll_id,)))


def generic_results_view(request, poll_id: int):
    """Redirect to poll's main vote method's results"""
    
    try:
        # Retrieve poll
        poll: PollModel = PollService.get_poll_by_id(poll_id)
    except Exception:
        raise Http404(f"Poll with id {poll_id} not found.")
    
    # redirect to proper vote method's results
    if poll.poll_type == PollModel.PollType.MAJORITY_JUDJMENT:
        return HttpResponseRedirect(reverse('apps.votes_results:majority_judgment_results', args=(poll_id,)))
    else:
        return HttpResponseRedirect(reverse('apps.votes_results:single_option_results', args=(poll_id,)))


# TODO: (maybe) use those pages to handle generalized parts (?)