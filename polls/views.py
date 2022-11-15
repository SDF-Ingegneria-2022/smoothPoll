from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render

from polls.business.dtos.poll_option_dto import PollOptionDto #type: ignore
from polls.business.dtos.poll_dto import dummy_poll #type: ignore
from polls.business.exceptions.poll_option_unvalid_exception import PollOptionUnvalidException #type: ignore




def index(request):
    """
    Hello world in our first app
    """

    return HttpResponse("Hello, world. You're at the polls index.")

def dummy(request: HttpRequest): 
    """
    Dummy poll page, here user can try to vote.
    """
     
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
        choice: PollOptionDto = dummy_poll.get_option_by_key(request.POST["vote"])
    except PollOptionUnvalidException:
        return HttpResponseBadRequest("Errore: l'opzione non è valida")

    return render(request, 'polls/vote_confirm.html', 
        {'poll': dummy_poll, 'choice': choice})
    
    
