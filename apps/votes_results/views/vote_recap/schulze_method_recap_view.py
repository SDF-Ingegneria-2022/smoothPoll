from django.http import Http404, HttpRequest, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from apps.polls_management.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
from apps.polls_management.models.poll_model import PollModel

from apps.polls_management.services.poll_service import PollService
from apps.votes_results.exceptions.vote_does_not_exixt_exception import VoteDoesNotExistException
from apps.votes_results.services.majority_judgment_vote_service import MajorityJudjmentVoteService
from apps.votes_results.views.vote.majority_judgment_vote_view import SESSION_MJ_SUBMIT_ID, SESSION_MJ_VOTE_SUBMIT_ERROR


def schulze_method_recap_view(request: HttpRequest, poll_id: int):
    """Submit the vote.
    Args:
        request (HttpRequest): Request object.
        poll_id (int): The poll id.
    Returns:
        HttpResponseRedirect: Redirect to the poll page.
        HttpResponse: Rendered confirm page.
    """

    # GET REQUEST --> I wanna render a page wich shows performed vote
    # (reloadable as many times user wants)

    try:
        # Retrieve poll
        poll: PollModel = PollService.get_poll_by_id(poll_id)
    except Exception:
        raise Http404(f"Poll with id {poll_id} not found.")

    # redirect to details page if poll is not yet open
    if not poll.is_open() or poll.is_closed():
        return HttpResponseRedirect(reverse('apps.polls_management:poll_details', args=(poll_id,)))
    
    vote = request.session.get("vote-submit-id")
    
    """
    
    # Retrieve session saved vote ID
    vote_id = request.session.get("vote-submit-id")
    if vote_id is None:
        request.session[SESSION_SINGLE_OPTION_VOTE_SUBMIT_ERROR] = "Errore! Non hai ancora espresso " \
            + "nessuna scelta. Usa questo form per esprimere la tua preferenza."
        return HttpResponseRedirect(reverse('apps.votes_results:single_option_vote', args=(poll_id,)))

    # retrieve vote 
    try:
        vote = SingleOptionVoteService.get_vote_by_id(vote_id)
    except VoteDoesNotExistException:
        request.session[SESSION_SINGLE_OPTION_VOTE_SUBMIT_ERROR] = "Errore! Non hai ancora espresso " \
            + "nessuna scelta. Usa questo form per esprimere la tua preferenza."
        return HttpResponseRedirect(reverse('apps.votes_results:single_option_vote', args=(poll_id,)))
    
    # show confirm page
    mj_vote_counter: SingleOptionVoteCounter = None
    
    if poll.is_votable_w_so_and_mj():
        mj_vote_counter: SingleOptionVoteCounter = SingleOptionVoteCounter(poll)

    # Clean session data for token validation if poll is not also votable with majority
    # if not poll.is_votable_w_so_and_mj():
    #     if request.session.get(SESSION_TOKEN_USED) is not None:
    #         del request.session[SESSION_TOKEN_USED]
    """
        
    return render(request, 'votes_results/schulze_method_recap.html', {'vote': vote,
                                                                      })



