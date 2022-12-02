from typing import List
from django.http import Http404  
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseServerError, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
from polls.classes.majority_poll_result_data import MajorityPollResultData
from polls.classes.poll_result import PollResult, PollResultVoice
from polls.classes.poll_result import PollResult
from polls.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
from polls.exceptions.vote_does_not_exixt_exception import VoteDoesNotExistException
from polls.models.majority_vote_model import MajorityVoteModel
from polls.models.poll_model import PollModel
from polls.models.poll_option_model import PollOptionModel
from polls.services.majority_vote_service import MajorityVoteService
from polls.services.poll_service import PollService
from polls.exceptions.poll_option_unvalid_exception import PollOptionUnvalidException
from polls.services.vote_service import VoteService

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

    # Get eventual error message and clean it
    eventual_error = request.session.get('vote-submit-error')
    if eventual_error is not None:
        del request.session['vote-submit-error']
    
    # Render vote form (with eventual error message)
    return render(request, 
                'polls/vote.html', 
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
            return HttpResponseRedirect(reverse('polls:get_poll', args=(poll_id,)))

        # retrieve vote 
        try:
            vote = VoteService.get_vote_by_id(vote_id)
        except VoteDoesNotExistException:
            request.session['vote-submit-error'] = "Errore! Non hai ancora caricato " \
                + "nessun voto. Usa questo form per esprimere la tua preferenza."
            return HttpResponseRedirect(reverse('polls:get_poll', args=(poll_id,)))
        
        # show confirm page
        return render(request, 'polls/vote_confirm.html', {'vote': vote})

    # POST REQUEST --> I wanna save the vote, save it in session and reload
    # this request as a GET one (so user will be able to refresh without
    # submitting again)

    # Check method is post.
    if request.method != "POST":
        request.session['vote-submit-error'] = "Errore! Il voto deve essere " \
            + "inviato tramite l'apposito form. Se continui a vedere questo " \
            + "messaggio contatta gli sviluppatori."
        return HttpResponseRedirect(reverse('polls:get_poll', args=(poll_id,)))
    
    # Check is passed any data.
    if 'vote' not in request.POST:
        request.session['vote-submit-error'] = "Errore! Per confermare il voto " \
            + "devi esprimere una preferenza."
        return HttpResponseRedirect(reverse('polls:get_poll', args=(poll_id,)))

    # Perform vote and handle missing vote or poll exception.
    try:
        vote = VoteService.perform_vote(poll_id, request.POST["vote"])
    except PollOptionUnvalidException:
        request.session['vote-submit-error'] = "Errore! Il voto deve essere " \
            + "inviato tramite l'apposito form. Se continui a vedere questo " \
            + "messaggio contatta gli sviluppatori."
        return HttpResponseRedirect(reverse('polls:get_poll', args=(poll_id,)))
    except PollDoesNotExistException:
        raise Http404

    # Clean eventual error session.
    if request.session.get('vote-submit-error') is not None:
        del request.session['vote-submit-error']

    # Save user vote in session (so when I re-render with GET I have the vote).
    request.session['vote-submit-id'] = vote.id

    # RE-direct to get request.
    return HttpResponseRedirect(reverse('polls:submit_vote', args=(poll_id, )))    

def results(request: HttpRequest, poll_id: int):
    """Render page with results.
    Args:
        request (HttpRequest): Request object.
        poll_id (int): The poll id.
    Returns:
        HttpResponse: Rendered results page.
        HttpResponseServerError: If DB is not initialized.
    """
    try:
        poll_results: PollResult = VoteService.calculate_result(poll_id)
    except PollDoesNotExistException:
        raise Http404
    except Exception:
        # Internal error: you should inizialize DB first (error 500)
        return HttpResponseServerError("Dummy survey is not initialized. Please see README.md and create it.")

    return render(request, 'polls/results.html', 
        
        {'poll_results': poll_results}
        )

def dummy_majority(request: HttpRequest): 
    """
    Dummy poll page, here user can try to vote.
    """
    try:
        poll = PollModel.objects.filter(poll_type='majority_vote').first()
    except Exception:
        raise Http404

    return render(request, 'polls/majority-vote.html', {'poll': poll})

def majority_vote_submit(request: HttpRequest, poll_id: int):
    """Render page with confirmation of majority vote validation."""

    ratings: List[dict] = []
    #poll: PollModel = PollModel.objects.filter(poll_id=poll_id)
    print(request.POST.items())
    for key, value in request.POST.items():
        if not key == 'csrfmiddlewaretoken':
            rating: dict = {}
            rating["poll_choice_id"] = int(key)
            rating["rating"] = int(value)
            ratings.append(rating)

    try:
        vote: MajorityVoteModel = MajorityVoteService.perform_vote(ratings, poll_id=str(poll_id))
    except Exception as e:
        raise Http404
    print(vote.judgments())
    return render(request, 'polls/vote-majority-confirm.html', {'vote': vote})

def majority_vote_results(request: HttpRequest, poll_id: int):
    """Render page with majority poll results"""

    try:
        poll_results: List[MajorityPollResultData] = MajorityVoteService.calculate_result(poll_id=str(poll_id))
    except PollDoesNotExistException:
        raise Http404
    except Exception:
        # Internal error: you should inizialize DB first (error 500)
        return HttpResponseServerError("Dummy survey is not initialized. Please see README.md and create it.")

    return render(request, 'polls/majority-results.html', 
        
        {'poll_results': poll_results}
        )

def all_polls(request: HttpRequest):
    """
    Render page with all polls.
    """
    try:
        page_information: str = request.GET.get('page')
        per_page: int = int(request.GET.get('per_page'))
    except TypeError:
        page_information = '1'
        per_page = 10
    
    paginator: Paginator = PollService.get_paginated_polls(per_page)

    if page_information == 'last':
        page = paginator.num_pages
    else:
        page: int = int(page_information)
    
    return render(  request, 
                    'polls/all_polls.html', 
                    {
                    'per_page': per_page,
                    'page': paginator.page(page)
                    }
                )

