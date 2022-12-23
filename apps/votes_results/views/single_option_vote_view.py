from django.http import Http404  
from django.http import HttpRequest, HttpResponseServerError, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from apps.polls_management.classes.poll_result import PollResult
from apps.polls_management.classes.poll_result import PollResult
from apps.polls_management.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
from apps.polls_management.exceptions.vote_does_not_exixt_exception import VoteDoesNotExistException
from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.services.poll_service import PollService
from apps.polls_management.exceptions.poll_option_unvalid_exception import PollOptionUnvalidException
from apps.polls_management.services.vote_service import VoteService

def get_poll(request: HttpRequest, poll_id: int): 
    """
    Get poll by id and render it.
    Args:
        request (HttpRequest): Request object.
        poll_id (int): The poll id.
    Returns:
        HttpResponse: Render the poll page.
    """

    try:
        # Retrieve poll
        poll: PollModel = PollService.get_poll_by_id(poll_id)
    except Exception:
        raise Http404(f"Poll with id {poll_id} not found.")

    if poll.poll_type == PollModel.PollType.MAJORITY_JUDJMENT:
        return HttpResponseRedirect(reverse('apps.votes_results:majority_judgment_vote', args=(poll_id,)))

    # Get eventual error message and clean it
    eventual_error = request.session.get('vote-submit-error')
    if eventual_error is not None:
        del request.session['vote-submit-error']
    
    # Render vote form (with eventual error message)
    return render(request, 
                'polls_management/vote.html', 
                { 
                    'poll': poll, 
                    'error': eventual_error 
                })
    
def submit_vote(request: HttpRequest, poll_id: int): 
    """Submit the vote.
    Args:
        request (HttpRequest): Request object.
        poll_id (int): The poll id.
    Returns:
        HttpResponseRedirect: Redirect to the poll page.
        HttpResponse: Rendered confirm page.
    """

    if request.method == "GET":

        # GET REQUEST --> I wanna render a page wich shows performed vote
        # (reloadable as many times user wants)

        # Retrieve session saved vote ID
        vote_id = request.session.get("vote-submit-id")
        if vote_id is None:
            request.session['vote-submit-error'] = "Errore! Non hai ancora caricato " \
                + "nessun voto. Usa questo form per esprimere la tua preferenza."
            return HttpResponseRedirect(reverse('apps.votes_results:single_option_vote', args=(poll_id,)))

        # retrieve vote 
        try:
            vote = VoteService.get_vote_by_id(vote_id)
        except VoteDoesNotExistException:
            request.session['vote-submit-error'] = "Errore! Non hai ancora caricato " \
                + "nessun voto. Usa questo form per esprimere la tua preferenza."
            return HttpResponseRedirect(reverse('apps.votes_results:single_option_vote', args=(poll_id,)))
        
        # show confirm page
        return render(request, 'polls_management/vote_confirm.html', {'vote': vote})

    # POST REQUEST --> I wanna save the vote, save it in session and reload
    # this request as a GET one (so user will be able to refresh without
    # submitting again)

    # Check method is post.
    if request.method != "POST":
        request.session['vote-submit-error'] = "Errore! Il voto deve essere " \
            + "inviato tramite l'apposito form. Se continui a vedere questo " \
            + "messaggio contatta gli sviluppatori."
        return HttpResponseRedirect(reverse('apps.votes_results:single_option_vote', args=(poll_id,)))
    
    # Check is passed any data.
    if 'vote' not in request.POST:
        request.session['vote-submit-error'] = "Errore! Per confermare il voto " \
            + "devi esprimere una preferenza."
        return HttpResponseRedirect(reverse('apps.votes_results:single_option_vote', args=(poll_id,)))

    # Perform vote and handle missing vote or poll exception.
    try:
        vote = VoteService.perform_vote(poll_id, request.POST["vote"])
    except PollOptionUnvalidException:
        request.session['vote-submit-error'] = "Errore! Il voto deve essere " \
            + "inviato tramite l'apposito form. Se continui a vedere questo " \
            + "messaggio contatta gli sviluppatori."
        return HttpResponseRedirect(reverse('apps.votes_results:single_option_vote', args=(poll_id,)))
    except PollDoesNotExistException:
        raise Http404

    # Clean eventual error session.
    if request.session.get('vote-submit-error') is not None:
        del request.session['vote-submit-error']

    # Save user vote in session (so when I re-render with GET I have the vote).
    request.session['vote-submit-id'] = vote.id

    # RE-direct to get request.
    return HttpResponseRedirect(reverse('apps.votes_results:single_option_recap', args=(poll_id, )))    

def results(request: HttpRequest, poll_id: int):
    """Render page with results.
    Args:
        request (HttpRequest): Request object.
        poll_id (int): The poll id.
    Returns:
        HttpResponse: Rendered results page.
        HttpResponseServerError: If DB is not initialized.
    """


    # if poll type is majority, we need to redirect 
    # to majority results page
    try:
        # Retrieve poll
        poll: PollModel = PollService.get_poll_by_id(poll_id)
    except Exception:
        raise Http404(f"Poll with id {poll_id} not found.")

    if poll.poll_type == PollModel.PollType.MAJORITY_JUDJMENT:
        return HttpResponseRedirect(reverse('apps.votes_results:majority_judgment_results', args=(poll_id,)))

    # regular results page 
    try:
        poll_results: PollResult = VoteService.calculate_result(poll_id)
    except PollDoesNotExistException:
        raise Http404
    except Exception:
        # Internal error: you should inizialize DB first (error 500)
        return HttpResponseServerError("Something got (slighly) terribly wrong. Please contact developers")

    return render(request, 'polls_management/results.html', 
        {'poll_results': poll_results}
        )
