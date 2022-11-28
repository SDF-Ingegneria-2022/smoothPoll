from typing import List
from django.http import Http404  
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseServerError, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
from polls.classes.poll_result import PollResult, PollResultVoice
from polls.classes.poll_result import PollResult
from polls.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
from polls.exceptions.vote_does_not_exixt_exception import VoteDoesNotExistException
from polls.services.poll_service import PollService
from polls.exceptions.poll_option_unvalid_exception import PollOptionUnvalidException
from polls.services.vote_service import VoteService

def dummy(request: HttpRequest): 
    """
    Dummy poll page, here user can try to vote.
    """

    try:
        # retrieve dummy poll
        dummy_poll = PollService.get_poll_by_id("1")
    except Exception:
        # internal error: you should inizialize DB first (error 500)
        return HttpResponseServerError("Dummy survey is not initialized. Please see README.md and create it.")

    # get eventual error message and clean it
    eventual_error = request.session.get('vote-submit-error')
    if eventual_error is not None:
        del request.session['vote-submit-error']

    # render vote form (with eventual error message)
    return render(request, 'polls/vote.html', 
        { 'poll': dummy_poll, 'error': eventual_error })
    
def submit_vote(request: HttpRequest): 
    """
    Submit the vote and get the result
    """

    if request.method == "GET":

        # GET REQUEST --> I wanna render a page wich shows performed vote
        # (reloadable as many times user wants)

        # retrieve session saved vote ID
        vote_id = request.session.get("vote-submit-id")
        if vote_id is None:
            request.session['vote-submit-error'] = "Errore! Non hai ancora caricato " \
                + "nessun voto. Usa questo form per esprimere la tua preferenza."
            return HttpResponseRedirect(reverse('polls:dummy'))

        # retrieve vote 
        try:
            vote = VoteService.get_vote_by_id(vote_id)
        except VoteDoesNotExistException:
            request.session['vote-submit-error'] = "Errore! Non hai ancora caricato " \
                + "nessun voto. Usa questo form per esprimere la tua preferenza."
            return HttpResponseRedirect(reverse('polls:dummy'))
        
        # show confirm page
        return render(request, 'polls/vote_confirm.html', {'vote': vote})

    # POST REQUEST --> I wanna save the vote, save it in session and reload
    # this request as a GET one (so user will be able to refresh without
    # submitting again)

    # check method is post
    if request.method != "POST":
        request.session['vote-submit-error'] = "Errore! Il voto deve essere " \
            + "inviato tramite l'apposito form. Se continui a vedere questo " \
            + "messaggio contatta gli sviluppatori."
        return HttpResponseRedirect(reverse('polls:dummy'))
    
    # check is passed any data
    if 'vote' not in request.POST:
        request.session['vote-submit-error'] = "Errore! Per confermare il voto " \
            + "devi esprimere una preferenza."
        return HttpResponseRedirect(reverse('polls:dummy'))

    # perform vote and handle missing vote or poll exception
    try:
        vote = VoteService.perform_vote(1, request.POST["vote"])
    except PollOptionUnvalidException:
        request.session['vote-submit-error'] = "Errore! Il voto deve essere " \
            + "inviato tramite l'apposito form. Se continui a vedere questo " \
            + "messaggio contatta gli sviluppatori."
        return HttpResponseRedirect(reverse('polls:dummy'))
    except PollDoesNotExistException:
        raise Http404

    # clean eventual error session 
    if request.session.get('vote-submit-error') is not None:
        del request.session['vote-submit-error']

    # save user vote in session (so when I re-render with GET I have the vote)
    request.session['vote-submit-id'] = vote.id

    # RE-direct to get request
    return HttpResponseRedirect(reverse('polls:submit_vote'))    

def results(request: HttpRequest):
    """
    #TODO: improve readability
    Render page with results. 
    """
    try:
        poll_results: PollResult = VoteService.calculate_result("1")
    except PollDoesNotExistException:
        raise Http404
    except Exception:
        # internal error: you should inizialize DB first (error 500)
        return HttpResponseServerError("Dummy survey is not initialized. Please see README.md and create it.")

    return render(request, 'polls/results.html', 
        # {'poll':sorted_options, 'question': poll_results.poll.question}
        {'poll_results': poll_results}
        )

def dummy_majority(request: HttpRequest): 
    """
    Dummy poll page, here user can try to vote.
    """

    try:
        poll_results: PollResult = VoteService.calculate_result("1")
        sorted_options: List[PollResultVoice] = poll_results.get_sorted_options()
    except Exception:
        # internal error: you should inizialize DB first (error 500)
        return HttpResponseServerError("Dummy survey is not initialized. Please see README.md and create it.")

    # render page for vote
    return render(request, 'polls/majority-vote.html', {'poll_results': poll_results})

def majority_results(request: HttpRequest):
    """
    #TODO: improve readability
    Render page with results. 
    """
    return render(request, 'polls/majority-results.html', 
        # {'poll':sorted_options, 'question': poll_results.poll.question}
        )

def all_polls(request: HttpRequest, page: int):
    """
    Render page with all polls.
    """
    paginator: Paginator = PollService.get_paginated_polls()
    
    return render(  request, 
                    'polls/all_polls.html', 
                    {
                    'page': paginator.page(page)
                    }
                )
