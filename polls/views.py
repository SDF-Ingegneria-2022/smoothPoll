from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from django.shortcuts import render
from .dtos.poll_option_dto import PollOptionDto 
from .dtos.poll_dto import PollDto
from .services.poll_service import PollService
from .exceptions.poll_option_unvalid_exception import PollOptionUnvalidException




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
        return HttpResponseBadRequest("Errore: il metodo deve essere post")
    
    if 'vote' not in request.POST:
        return HttpResponseBadRequest("Errore: manca il voto")

    try:
        # retrieve dummy poll
        dummy_poll: PollDto = PollService.get_by_id("1")
    except Exception:
        # internal error: you should inizialize DB first (error 500)
        return HttpResponseServerError("Dummy survey is not initialized. Please see README.md and create it.")

    try:
        choice: PollOptionDto = dummy_poll.get_option_by_key(request.POST["vote"])
    except PollOptionUnvalidException:
        return HttpResponseBadRequest("Errore: l'opzione selezionata non è valida")

    return render(request, 'polls/vote_confirm.html', 
        {'poll': dummy_poll, 'choice': choice})
    
    
