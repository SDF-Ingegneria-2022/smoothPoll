from typing import List
from django.http import Http404  
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseServerError, HttpResponseRedirect
from django.shortcuts import render
from polls.classes.poll_result import PollResult
from polls.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
from django.urls import reverse

from polls.models.vote_model import VoteModel
from polls.services.poll_service import PollService
from polls.exceptions.poll_option_unvalid_exception import PollOptionUnvalidException
from polls.services.vote_service import VoteService

def index(request):
    """
    Hello world in our first app
    """
    return HttpResponse("Hello, world. You're at the polls index.")

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

    eventual_error = request.session.get('vote-submit-error')
    if eventual_error is not None:
        del request.session['vote-submit-error']

    # render vote form (with eventual error message)
    return render(request, 'polls/vote.html', {
        'poll': dummy_poll, 
        'error': eventual_error
        })
    
def submit_vote(request: HttpRequest): 
    """
    Submit the vote and get the result
    """

    if request.method != "POST":
        request.session['vote-submit-error'] = "Errore! Il voto deve essere " \
            + "inviato tramite l'apposito form. Se continui a vedere questo " \
            + "messaggio contatta gli sviluppatori."
        return HttpResponseRedirect(reverse('polls:dummy'))
    
    if 'vote' not in request.POST:
        request.session['vote-submit-error'] = "Errore! Per confermare il voto " \
            + "devi esprimere una preferenza."
        return HttpResponseRedirect(reverse('polls:dummy'))

    try:
        vote: VoteModel = VoteService.perform_vote(1, request.POST["vote"])
    except PollOptionUnvalidException:
        request.session['vote-submit-error'] = "Errore! Il voto deve essere " \
            + "inviato tramite l'apposito form. Se continui a vedere questo " \
            + "messaggio contatta gli sviluppatori."
        return HttpResponseRedirect(reverse('polls:dummy'))
        
    except PollDoesNotExistException:
        raise Http404

    # clean session error
    if request.session.get('vote-submit-error') is not None:
        del request.session['vote-submit-error']

    return render(request, 'polls/vote_confirm.html', {'vote': vote})
    

def results(request: HttpRequest):
    """
    #TODO: improve readability
    Render page with results. 
    """
    try:
        poll_results: PollResult = VoteService.calculate_result("1")
    except PollDoesNotExistException:
        pass # TODO: add error 404 error page
    except Exception:
        # internal error: you should inizialize DB first (error 500)
        return HttpResponseServerError("Dummy survey is not initialized. Please see README.md and create it.")

    return render(request, 'polls/results.html', 
        # {'poll':sorted_options, 'question': poll_results.poll.question}
        {'poll_results': poll_results}
        )


def all_polls(request: HttpRequest):
    return render(request, 'polls/all_polls.html', {'some_list': [x for x in range(5)]})
