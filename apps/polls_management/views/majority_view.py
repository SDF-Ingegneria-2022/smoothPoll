from typing import List
from django.http import Http404  
from django.http import HttpRequest, HttpResponseServerError, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from apps.polls_management.classes.majority_poll_result_data import MajorityPollResultData
from apps.polls_management.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
from apps.polls_management.exceptions.poll_not_yet_voted_exception import PollNotYetVodedException
from apps.polls_management.exceptions.poll_option_rating_unvalid_exception import PollOptionRatingUnvalidException
from apps.polls_management.models.majority_vote_model import MajorityVoteModel
from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.services.majority_vote_service import MajorityVoteService
from apps.polls_management.services.poll_service import PollService


def dummy_majority(request: HttpRequest, poll_id=None): 
    """
    Dummy poll page, here user can try to vote.
    
    """

    if poll_id is None:
        try:
            poll = PollModel.objects.filter(poll_type='majority_judjment').first()
        except Exception:
            raise HttpResponseServerError("Error: if you are seeing this message " \
                + "it means developer didn't seeded the database with a majority " \
                + "judgment dummy poll")
    else: 
        try:
            poll = PollService.get_poll_by_id(poll_id)
        except PollDoesNotExistException:
            raise Http404()

    if poll.poll_type != PollModel.PollType.MAJORITY_JUDJMENT:
        raise Http404()

    options_selected = request.session.get('majvote-submit-error')
    if options_selected is not None:
        del request.session['majvote-submit-error']
    

    return render(
                    request, 
                    'polls_management/majority-vote.html', 
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
        return HttpResponseRedirect(reverse('apps.votes_results:dummy_majority' ))
    except Exception as e:
        raise Http404
    return render(request, 'polls_management/vote-majority-confirm.html', {'vote': vote})

def majority_vote_results(request: HttpRequest, poll_id: int):
    """Render page with majority poll results"""

    # poll should be Majority type
    try:
        poll = PollService.get_poll_by_id(poll_id)
    except PollDoesNotExistException:
        raise Http404()

    if poll.poll_type != PollModel.PollType.MAJORITY_JUDJMENT:
        raise Http404()
    
    try:
        poll_results: List[MajorityPollResultData] = MajorityVoteService.calculate_result(poll_id=str(poll_id))
    except PollDoesNotExistException:
        raise Http404
    except PollNotYetVodedException:
        poll_results = None


    # except Exception:
    #     # Internal error: you should inizialize DB first (error 500)
    #     return HttpResponseServerError("Dummy survey is not initialized. Please see README.md and create it.")

    return render(request, 'polls_management/majority-results.html', {
        'poll_results': poll_results, 
        'poll': PollModel.objects.get(id=poll_id)
        })
