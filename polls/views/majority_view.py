from typing import List
from django.http import Http404  
from django.http import HttpRequest, HttpResponseServerError, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from polls.classes.majority_poll_result_data import MajorityPollResultData
from polls.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
from polls.exceptions.poll_option_rating_unvalid_exception import PollOptionRatingUnvalidException
from polls.models.majority_vote_model import MajorityVoteModel
from polls.models.poll_model import PollModel
from polls.services.majority_vote_service import MajorityVoteService


def dummy_majority(request: HttpRequest): 
    """
    Dummy poll page, here user can try to vote.
    
    """
    options_selected = request.session.get('majvote-submit-error')
    if options_selected is not None:
        del request.session['majvote-submit-error']

    try:
        poll = PollModel.objects.filter(poll_type='majority_vote').first()
    except Exception:
        raise HttpResponseServerError("Error: if you are seeing this message " \
            + "it means developer didn't seeded the database with a majority " \
            + "judgment dummy poll")

    return render(
                    request, 
                    'polls/majority-vote.html', 
                    {
                        'poll': poll, 
                        
                        'error': {
                                     'message': "Attenzione! Non è stata selezionata nessuna opzione.",
                                     'options_selected': options_selected,
                                 },
                        'prova': {'1': {
                                        '2':2
                                        }
                                }
                        }
                    )        

def majority_vote_submit(request: HttpRequest, poll_id: int):
    """Render page with confirmation of majority vote validation."""

    ratings: List[dict] = []
    session_object: dict = {
        'id': []
    }
    #poll: PollModel = PollModel.objects.filter(poll_id=poll_id)
    for key, value in request.POST.items():
        if not key == 'csrfmiddlewaretoken':
            rating: dict = {}
            rating["poll_choice_id"] = int(key)
            rating["rating"] = int(value)
            ratings.append(rating)
            session_object['id'].append(int(key))
            session_object[int(key)] =  int(value)


    try:
        vote: MajorityVoteModel = MajorityVoteService.perform_vote(ratings, poll_id=str(poll_id))
    except PollOptionRatingUnvalidException:
       
        request.session['majvote-submit-error'] = session_object
        return HttpResponseRedirect(reverse('polls:dummy_majority' ))
    except Exception as e:
        raise Http404
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
