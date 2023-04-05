from apps.polls_management.classes.poll_token_validation.token_validation import TokenValidation
from apps.polls_management.models.poll_option_model import PollOptionModel
from apps.polls_management.services.poll_token_service import PollTokenService
from apps.votes_results.classes.majority_poll_result_data import MajorityPollResultData
from apps.polls_management.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
from apps.votes_results.classes.vote_consistency.check_consistency_session import CheckConsistencySession
from apps.votes_results.exceptions.poll_not_yet_voted_exception import PollNotYetVodedException
from apps.votes_results.exceptions.poll_option_rating_unvalid_exception import PollOptionRatingUnvalidException
from apps.votes_results.exceptions.vote_does_not_exixt_exception import VoteDoesNotExistException
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
from sesame.utils import get_user, get_token
from sesame.decorators import authenticate

from apps.votes_results.views.single_option_vote_view import SESSION_SINGLE_OPTION_VOTE_ID

SESSION_MJ_GUIDE_ALREADY_VIWED = 'mj-guide-already-viewed'
SESSION_MJ_VOTE_SUBMIT_ERROR = 'majvote-submit-error'
SESSION_MJ_SUBMIT_ID = 'majvote-submit-id'
SESSION_CONSISTENCY_CHECK = 'consistency-check'

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
        
        # check if the poll is accessed by a single poll url rather than the link with the token
        if poll.is_votable_token() and request.session.get('token_used') is None:
            return render(request, 'polls_management/token_poll_redirect.html', {'poll': poll})
        elif poll.is_votable_token() and request.session.get('token_used') and poll.votable_mj:
            if TokenValidation.validate(request.session.get('token_used')):
                return HttpResponseRedirect(reverse('apps.votes_results:single_option_vote', args=(poll_id,)))

        if ((poll.poll_type != PollModel.PollType.MAJORITY_JUDJMENT and not poll.votable_mj) or
            ( poll.poll_type == PollModel.PollType.SINGLE_OPTION and
              request.session.get(SESSION_SINGLE_OPTION_VOTE_ID) is None and 
              not poll.is_votable_token())
            ):
            raise Http404()

        options_selected = request.session.get(SESSION_MJ_VOTE_SUBMIT_ERROR)
        if options_selected is not None:
            del request.session[SESSION_MJ_VOTE_SUBMIT_ERROR]
        
        guide_already_viwed: bool = request.session.get(SESSION_MJ_GUIDE_ALREADY_VIWED)

        if request.session.get(SESSION_MJ_GUIDE_ALREADY_VIWED) is None:
            request.session[SESSION_MJ_GUIDE_ALREADY_VIWED] = True
        
        if poll.poll_type == PollModel.PollType.SINGLE_OPTION and poll.votable_mj and request.session.get(SESSION_SINGLE_OPTION_VOTE_ID) is not None:
            vote_single_option: PollOptionModel = PollOptionModel.objects.get(id=request.session.get(SESSION_SINGLE_OPTION_VOTE_ID))
            request.session['os_to_mj'] = vote_single_option.value

        return render(request, 'votes_results/majority_judgment_vote.html', {
            'poll': poll, 
            'error': {
                'message': "Attenzione! Non è stata selezionata nessuna opzione.",
                'options_selected': options_selected,
            }, 
            'guide_already_viwed': guide_already_viwed,
            'consistency_check': request.session.get(SESSION_CONSISTENCY_CHECK),
            'single_option' : request.session.get('os_to_mj'),
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
            return HttpResponseRedirect(reverse('apps.polls_management:poll_details', args=(poll_id,)))
        
        ratings: List[dict] = []
        session_object: dict = {
            'id': []
        }
        
        for key, value in request.POST.items():
           
            if not key == 'csrfmiddlewaretoken':
                rating: dict = {}
                rating["poll_choice_id"] = int(key)
                rating["rating"] = int(value)
                ratings.append(rating)
                session_object['id'].append(int(key))
                session_object[int(key)] =  int(value)
        

        # Single option vote consistency check
        check_consistency_session: CheckConsistencySession = CheckConsistencySession(request)
        if  (not request.session.get(SESSION_CONSISTENCY_CHECK) and # Check used if user has already seen the consistency check
            check_consistency_session.check_consistency(poll, ratings, SESSION_SINGLE_OPTION_VOTE_ID, SESSION_CONSISTENCY_CHECK)):
            return HttpResponseRedirect(reverse('apps.votes_results:majority_judgment_vote', args=(poll_id,)))    
        
        try:
            vote: MajorityVoteModel = MajorityJudjmentVoteService.perform_vote(ratings, poll_id=str(poll_id))

            # invalidation of token if vote is successful
            if request.session.get('token_used') is not None:
                try:
                    token_poll = request.session.get('token_used')
                except Exception:
                    raise Http404(f"Token associated with user {token_poll.token_user} not found.")
                PollTokenService.check_majority_option(token_poll)

            # Clear session if the mj vote is performed
            check_consistency_session.clear_session([SESSION_SINGLE_OPTION_VOTE_ID, SESSION_CONSISTENCY_CHECK])
            
        except PollOptionRatingUnvalidException:
        
            request.session[SESSION_MJ_VOTE_SUBMIT_ERROR] = session_object
            return HttpResponseRedirect(reverse('apps.votes_results:majority_judgment_vote', args=(poll_id,)))
        except Exception as e:
            raise Http404

        # Clean session data for token validation
        if request.session.get('token_used') is not None:
            del request.session['token_used']

        # Clean session data for single option to majority control
        if request.session.get('os_tom_mj') is not None:
            del request.session['os_to_mj']

        # Clean eventual error session.
        if request.session.get(SESSION_MJ_VOTE_SUBMIT_ERROR) is not None:
            del request.session[SESSION_MJ_VOTE_SUBMIT_ERROR]

        # Save user vote in session
        request.session[SESSION_MJ_SUBMIT_ID] = vote.id

        # Redirect to get request.
        return HttpResponseRedirect(reverse('apps.votes_results:majority_judgment_recap', args=(poll_id, )))



def majority_judgment_recap_view(request: HttpRequest, poll_id: int):
    """Render page with confirmation of majority vote validation."""

    try:
        poll = PollService.get_poll_by_id(poll_id)
    except PollDoesNotExistException:
        raise Http404()
        
    # Redirect to details page if poll is not yet open
    if not poll.is_open() or poll.is_closed():
        return HttpResponseRedirect(reverse('apps.polls_management:poll_details', args=(poll_id,)))

    # Retrieve session saved vote ID
    vote_id = request.session.get(SESSION_MJ_SUBMIT_ID)
    if vote_id is None:
        request.session[SESSION_MJ_VOTE_SUBMIT_ERROR] = "Errore! Non hai ancora espresso " \
            + "nessun giudizio. Usa questo form per esprimere la tua preferenza."
        return HttpResponseRedirect(reverse('apps.votes_results:majority_judgment_vote', args=(poll_id,)))

    # Retrieve vote 
    try:
        vote = MajorityJudjmentVoteService.get_vote_by_id(vote_id)
    except VoteDoesNotExistException:
        request.session[SESSION_MJ_VOTE_SUBMIT_ERROR] = "Errore! Non hai ancora espresso " \
            + "nessun giudizio. Usa questo form per esprimere la tua preferenza."
        return HttpResponseRedirect(reverse('apps.votes_results:majority_judgment_vote', args=(poll_id,)))

    return render(request, 'votes_results/majority_judgment_recap.html', {'vote': vote})

def majority_judgment_results_view(request: HttpRequest, poll_id: int):
    """Render page with majority poll results"""

    # Poll should be Majority type
    try:
        poll = PollService.get_poll_by_id(poll_id)
    except PollDoesNotExistException:
        raise Http404()

    # Redirect to details page if poll is not yet open
    if not poll.is_open():
        return HttpResponseRedirect(reverse('apps.polls_management:poll_details', args=(poll_id,)))

    if poll.poll_type != PollModel.PollType.MAJORITY_JUDJMENT and poll.votable_mj != True:
        raise Http404()
    
    try:
        poll_results: List[MajorityPollResultData] = MajorityJudjmentVoteService.calculate_result(poll_id=str(poll_id))
    except PollDoesNotExistException:
        raise Http404()
    except PollNotYetVodedException:
        poll_results = None

    return render(request, 'votes_results/majority_judgment_results.html', {
        'poll_results': poll_results, 
        'poll': PollModel.objects.get(id=poll_id),
        'poll_info_to_view': {
            'name': False,
            'question': False,
            'choices': False,
            'status': True,
            'datetimes': True,
            'type': True,
        }
        })
