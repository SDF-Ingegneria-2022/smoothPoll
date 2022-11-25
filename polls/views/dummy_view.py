from typing import List
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
     
    # render page for vote
    return render(request, 'polls/vote.html', {'poll': dummy_poll})
    
def submit_vote(request: HttpRequest): 
    """
    Submit the vote and get the result
    """

    if request.method != "POST":
        return HttpResponseBadRequest("Error: method should be post")
    
    if 'vote' not in request.POST:
        return HttpResponseRedirect(reverse('polls:vote_error'))

    try:
        vote: VoteModel = VoteService.perform_vote(1, request.POST["vote"])
    except PollOptionUnvalidException:
        pass # TODO: add error error page
    except PollDoesNotExistException:
        pass # TODO: add error 404 error page

    return render(request, 'polls/vote_confirm.html', 
        {'vote': vote}
        )
    

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


def vote_error(request: HttpRequest):
    """
    Error page for vote
    """
    #TODO: temporary hardcoded poll retrieval. It should be retrieved from DB according to the poll id
    dummy_poll = PollService.get_poll_by_id("1")
    return render(request, 'polls/vote.html', 
        {
            'poll': dummy_poll, 
            'error': "Attenzione! Non è stata espressa nessuna preferenza!"
        })


def all_polls(request: HttpRequest):
    return render(request, 'polls/all_polls.html', {'some_list': [x for x in range(5)]})
