from typing import List
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseServerError, HttpResponseRedirect
from django.shortcuts import render
from polls.classes.poll_result import PollResult, PollResultVoice
from polls.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
from django.urls import reverse

from polls.models.vote_model import VoteModel
from .dtos.poll_option_dto import PollOptionDto 
from .dtos.poll_dto import PollDto
from .services.poll_service import PollService
from .exceptions.poll_option_unvalid_exception import PollOptionUnvalidException
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
        dummy_poll: PollDto = PollService.get_by_id("1")
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
        pass
    except PollDoesNotExistException:
        pass

    return render(request, 'polls/vote_confirm.html', 
        # {'poll': vote.poll(), 'choice': vote.poll_option}
        {'vote': vote}
        )
    

def results(request: HttpRequest):
    """
    #TODO: improve readability
    Render page with results. 
    """
    try:
        poll_results: PollResult = VoteService.calculate_result("1")
        sorted_options: List[PollResultVoice] = poll_results.get_sorted_options()
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
    dummy_poll: PollDto = PollService.get_by_id("1")
    return render(request, 'polls/vote_error.html', {'poll': dummy_poll})

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
