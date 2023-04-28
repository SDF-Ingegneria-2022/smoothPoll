
from django.http import Http404, HttpRequest, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from apps.polls_management.exceptions.poll_does_not_exist_exception import PollDoesNotExistException

from apps.polls_management.services.poll_service import PollService
from apps.votes_results.exceptions.vote_does_not_exixt_exception import VoteDoesNotExistException
from apps.votes_results.services.majority_judgment_vote_service import MajorityJudjmentVoteService
from apps.votes_results.views.vote.majority_judgment_vote_view import SESSION_MJ_SUBMIT_ID, SESSION_MJ_VOTE_SUBMIT_ERROR


def majority_judgment_recap_view(request: HttpRequest, poll_id: int):
    """Render page with confirmation of majority vote validation."""

    try:
        poll = PollService.get_poll_by_id(poll_id)
    except PollDoesNotExistException:
        raise Http404()
        
    # Redirect to details page if poll is not yet open
    if not poll.is_open() or poll.is_closed():
        return HttpResponseRedirect(reverse('apps.polls_management:poll_details', args=(poll_id,)))

    # Retrieve session saved vote ID
    vote_id = request.session.get(SESSION_MJ_SUBMIT_ID)
    if vote_id is None:
        request.session[SESSION_MJ_VOTE_SUBMIT_ERROR] = "Errore! Non hai ancora espresso " \
            + "nessun giudizio. Usa questo form per esprimere la tua preferenza."
        return HttpResponseRedirect(reverse('apps.votes_results:majority_judgment_vote', args=(poll_id,)))

    # Retrieve vote 
    try:
        vote = MajorityJudjmentVoteService.get_vote_by_id(vote_id)
    except VoteDoesNotExistException:
        request.session[SESSION_MJ_VOTE_SUBMIT_ERROR] = "Errore! Non hai ancora espresso " \
            + "nessun giudizio. Usa questo form per esprimere la tua preferenza."
        return HttpResponseRedirect(reverse('apps.votes_results:majority_judgment_vote', args=(poll_id,)))
    
    # Clean session data for token validation
    # if request.session.get('token_used') is not None:
    #     del request.session['token_used']

    return render(request, 'votes_results/majority_judgment_recap.html', {'vote': vote})

