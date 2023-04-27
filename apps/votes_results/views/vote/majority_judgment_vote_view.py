from apps.polls_management.classes.poll_token_validation.token_validation import TokenValidation
from apps.polls_management.models.poll_option_model import PollOptionModel
from apps.polls_management.models.poll_token import PollTokens
from apps.polls_management.services.poll_token_service import PollTokenService
from apps.votes_results.classes.vote_consistency.check_consistency_session import CheckConsistencySession
from apps.votes_results.exceptions.poll_option_rating_unvalid_exception import PollOptionRatingUnvalidException
from apps.polls_management.models.majority_vote_model import MajorityVoteModel
from apps.polls_management.models.poll_model import PollModel
from apps.votes_results.services.majority_judgment_vote_service import MajorityJudjmentVoteService

from typing import List
from django.http import Http404, HttpResponse  
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from apps.votes_results.views.vote.single_option_vote_view import SESSION_SINGLE_OPTION_VOTE_ID
from apps.votes_results.views.vote.vote_view_schema import VoteViewSchema

SESSION_MJ_GUIDE_ALREADY_VIWED = 'mj-guide-already-viewed'
SESSION_MJ_VOTE_SUBMIT_ERROR = 'majvote-submit-error'
SESSION_MJ_SUBMIT_ID = 'majvote-submit-id'
SESSION_CONSISTENCY_CHECK = 'consistency-check'
SESSION_TOKEN_USED = 'token_used'

class MajorityJudgmentVoteView(VoteViewSchema):
    """View to handle Majority Judgment vote process"""

    def get_votemethod(self) -> PollModel.PollType:
        return PollModel.PollType.MAJORITY_JUDJMENT
    
    def get_recap_page_url_name(self) -> str:
        return 'apps.votes_results:majority_judgment_recap'
    
    def render_vote_form(self, request: HttpRequest) -> HttpResponse:

        # TODO: remove this if is not necessary
        if (
                self.poll().poll_type != PollModel.PollType.MAJORITY_JUDJMENT and 
                not self.poll().is_votable_w_so_and_mj()
            ) or \
            ( 
                self.poll().poll_type == PollModel.PollType.SINGLE_OPTION and
                request.session.get(SESSION_SINGLE_OPTION_VOTE_ID) is None and 
                not self.poll().is_votable_token() and not self.poll().is_votable_google()
            ):

            raise Http404()
        
        options_selected = request.session.get(SESSION_MJ_VOTE_SUBMIT_ERROR)
        if options_selected is not None:
            del request.session[SESSION_MJ_VOTE_SUBMIT_ERROR]
        
        guide_already_viwed: bool = request.session.get(SESSION_MJ_GUIDE_ALREADY_VIWED)

        if request.session.get(SESSION_MJ_GUIDE_ALREADY_VIWED) is None:
            request.session[SESSION_MJ_GUIDE_ALREADY_VIWED] = True
        
        if self.poll().poll_type == PollModel.PollType.SINGLE_OPTION and \
            self.poll().is_votable_w_so_and_mj() and \
            request.session.get(SESSION_SINGLE_OPTION_VOTE_ID) is not None:

            vote_single_option: PollOptionModel = PollOptionModel.objects.get(id=request.session.get(SESSION_SINGLE_OPTION_VOTE_ID))
            request.session['os_to_mj'] = vote_single_option.value

        return render(request, 'votes_results/majority_judgment_vote.html', {
            'poll': self.poll(), 
            'error': {
                'message': "Attenzione! Non è stata selezionata nessuna opzione.",
                'options_selected': options_selected,
            }, 
            'guide_already_viwed': guide_already_viwed,
            'consistency_check': request.session.get(SESSION_CONSISTENCY_CHECK),
            'single_option' : request.session.get('os_to_mj'),
            })

    def perform_vote_or_redirect_to_form(self, request: HttpRequest) -> HttpResponse:
        
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
        if  (not request.session.get(SESSION_CONSISTENCY_CHECK) and 
             # Check used if user has already seen the consistency check
            check_consistency_session.check_consistency(
                self.poll(), ratings, 
                SESSION_SINGLE_OPTION_VOTE_ID, 
                SESSION_CONSISTENCY_CHECK )):
            
            return HttpResponseRedirect(reverse(
                'apps.votes_results:majority_judgment_vote', 
                args=(self.poll().id,)))    
        
        try:
            vote: MajorityVoteModel = MajorityJudjmentVoteService.perform_vote(
                ratings, poll_id=str(self.poll().id))
        except PollOptionRatingUnvalidException:
        
            request.session[SESSION_MJ_VOTE_SUBMIT_ERROR] = session_object
            return HttpResponseRedirect(reverse(
                'apps.votes_results:majority_judgment_vote', 
                args=(self.poll().id, )))
        except Exception as e:
            raise Http404
        
        
        # Clear session if the mj vote is performed
        check_consistency_session.clear_session([
            SESSION_SINGLE_OPTION_VOTE_ID, 
            SESSION_CONSISTENCY_CHECK
            ])
        
        # Clean session data for single option to majority control
        if request.session.get('os_to_mj') is not None:
            del request.session['os_to_mj']

        # Clean eventual error session.
        if request.session.get(SESSION_MJ_VOTE_SUBMIT_ERROR) is not None:
            del request.session[SESSION_MJ_VOTE_SUBMIT_ERROR]

        # Save user vote in session
        request.session[SESSION_MJ_SUBMIT_ID] = vote.id

        return None
