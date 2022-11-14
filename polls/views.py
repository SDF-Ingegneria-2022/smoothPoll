from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render

from polls.logic.classes.poll_option import PollOption
from polls.logic.classes.poll import Poll, dummy_poll



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

    options = {
        '1': "Opzione 1", 
        '2': "Opzione 2", 
        '3': "Opzione 3"
    }

    choice = options.get(request.POST['vote'])

    return render(request, 'polls/vote_confirm.html', 
    {'poll': dummy_poll, 'choice': choice})
    
    
