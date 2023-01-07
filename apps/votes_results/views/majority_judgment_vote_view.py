from apps.polls_management.classes.majority_poll_result_data import MajorityPollResultData
from apps.polls_management.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
from apps.polls_management.exceptions.poll_not_yet_voted_exception import PollNotYetVodedException
from apps.polls_management.exceptions.poll_option_rating_unvalid_exception import PollOptionRatingUnvalidException
from apps.polls_management.exceptions.vote_does_not_exixt_exception import VoteDoesNotExistException
from apps.polls_management.models.majority_vote_model import MajorityVoteModel
from apps.polls_management.models.poll_model import PollModel
from apps.votes_results.services.majority_judgment_vote_service import MajorityJudjmentVoteService
from apps.polls_management.services.poll_service import PollService

from typing import List
from django.http import Http404  
from django.http import HttpRequest, HttpResponseServerError, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View

class MajorityJudgmentVoteView(View):
    """View to handle Majority Judgment vote process"""
    
    @staticmethod
    def __get_dummy_poll() -> PollModel:
        """Try to retrieve a dummy MJ poll"""

        try:
            return PollModel.objects.filter(poll_type='majority_judjment').first()
        except Exception:
            raise HttpResponseServerError("Error: if you are seeing this message " \
                + "it means developer didn't seeded the database with a majority " \
                + "judgment dummy poll")

    def get(self, request: HttpRequest, poll_id: int, *args, **kwargs):
        """Render the form wich permits user to vote"""

        if poll_id is None:
            # if poll_id is none I try retrieving a dummy poll
            poll = MajorityJudgmentVoteView.__get_dummy_poll()
        else: 
            try:
                poll = PollService.get_poll_by_id(poll_id)
            except PollDoesNotExistException:
                raise Http404()

        # redirect to details page if poll is not yet open
        if not poll.is_open() or poll.is_closed():
            return render(request, 'votes_results/poll_details.html', {'poll': poll})

        
        if poll.poll_type != PollModel.PollType.MAJORITY_JUDJMENT and poll.votable_mj != True:
            
            raise Http404()

        options_selected = request.session.get('majvote-submit-error')
        if options_selected is not None:
            del request.session['majvote-submit-error']
        
        return render(request, 'votes_results/majority_judgment_vote.html', {
            'poll': poll, 
            'error': {
                'message': "Attenzione! Non è stata selezionata nessuna opzione.",
                'options_selected': options_selected,
            }, 
            'prova': {'1': {'2':2 } }
            })    

    def post(self, request: HttpRequest, poll_id: int, *args, **kwargs):
        """Handle vote perform and redirect to recap (or 
        redirect to form w errors)"""

        try:
            poll = PollService.get_poll_by_id(poll_id)
        except PollDoesNotExistException:
            raise Http404()
        
        # redirect to details page if poll is not yet open
        if not poll.is_open() or poll.is_closed():
            return HttpResponseRedirect(reverse('apps.votes_results:poll_details', args=(poll_id,)))
        
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
            vote: MajorityVoteModel = MajorityJudjmentVoteService.perform_vote(ratings, poll_id=str(poll_id))
        except PollOptionRatingUnvalidException:
        
            request.session['majvote-submit-error'] = session_object
            return HttpResponseRedirect(reverse('apps.votes_results:majority_judgment_vote', args=(poll_id,)))
        except Exception as e:
            raise Http404

        # Clean eventual error session.
        if request.session.get('majvote-submit-error') is not None:
            del request.session['majvote-submit-error']

        # save user vote in session
        request.session['majvote-submit-id'] = vote.id

        # RE-direct to get request.
        return HttpResponseRedirect(reverse('apps.votes_results:majority_judgment_recap', args=(poll_id, )))



def majority_judgment_recap_view(request: HttpRequest, poll_id: int):
    """Render page with confirmation of majority vote validation."""

    try:
        poll = PollService.get_poll_by_id(poll_id)
    except PollDoesNotExistException:
        raise Http404()
        
    # redirect to details page if poll is not yet open
    if not poll.is_open() or poll.is_closed():
        return HttpResponseRedirect(reverse('apps.votes_results:poll_details', args=(poll_id,)))

    # Retrieve session saved vote ID
    vote_id = request.session.get("majvote-submit-id")
    if vote_id is None:
        request.session['majvote-submit-error'] = "Errore! Non hai ancora caricato " \
            + "nessun voto. Usa questo form per esprimere la tua preferenza."
        return HttpResponseRedirect(reverse('apps.votes_results:majority_judgment_vote', args=(poll_id,)))

    # retrieve vote 
    try:
        vote = MajorityJudjmentVoteService.get_vote_by_id(vote_id)
    except VoteDoesNotExistException:
        request.session['majvote-submit-error'] = "Errore! Non hai ancora caricato " \
            + "nessun voto. Usa questo form per esprimere la tua preferenza."
        return HttpResponseRedirect(reverse('apps.votes_results:majority_judgment_vote', args=(poll_id,)))

    return render(request, 'votes_results/majority_judgment_recap.html', {'vote': vote})

def majority_judgment_results_view(request: HttpRequest, poll_id: int):
    """Render page with majority poll results"""

    # poll should be Majority type
    try:
        poll = PollService.get_poll_by_id(poll_id)
    except PollDoesNotExistException:
        raise Http404()

    # redirect to details page if poll is not yet open
    if not poll.is_open():
        return HttpResponseRedirect(reverse('apps.votes_results:poll_details', args=(poll_id,)))

    if poll.poll_type != PollModel.PollType.MAJORITY_JUDJMENT and poll.votable_mj != True:
        raise Http404()
    
    try:
        poll_results: List[MajorityPollResultData] = MajorityJudjmentVoteService.calculate_result(poll_id=str(poll_id))
    except PollDoesNotExistException:
        raise Http404
    except PollNotYetVodedException:
        poll_results = None


    # except Exception:
    #     # Internal error: you should inizialize DB first (error 500)
    #     return HttpResponseServerError("Dummy survey is not initialized. Please see README.md and create it.")

    return render(request, 'votes_results/majority_judgment_results.html', {
        'poll_results': poll_results, 
        'poll': PollModel.objects.get(id=poll_id)
        })
