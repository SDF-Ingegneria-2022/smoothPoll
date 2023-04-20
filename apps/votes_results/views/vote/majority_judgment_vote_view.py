from apps.polls_management.classes.poll_token_validation.token_validation import TokenValidation
from apps.polls_management.models.poll_option_model import PollOptionModel
from apps.polls_management.models.poll_token import PollTokens
from apps.polls_management.services.poll_token_service import PollTokenService
from apps.votes_results.classes.majority_poll_result_data import MajorityPollResultData
from apps.polls_management.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
from apps.votes_results.classes.vote.vote_permissions_checker import VotePermissionsChecker
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


    def get(self, request: HttpRequest, poll_id: int, *args, **kwargs):
        """Render the form wich permits user to vote"""
        
        super().get(request, poll_id, *args, **kwargs)

        poll = self.vote_permission_checker.poll

        # check if the poll is accessed by a single poll url rather than the link with the token
        # if poll.is_votable_token() and request.session.get('token_used') is None:
        #     return render(request, 'polls_management/token_poll_redirect.html', {'poll': poll})
        # elif not TokenValidation.validate(request.session.get('token_used')):
        #         return render(request, 'polls_management/token_poll_redirect.html', {'poll': poll})
        # elif poll.is_votable_token() and request.session.get('token_used') and poll.is_votable_w_so_and_mj():
        #     if TokenValidation.validate(request.session.get('token_used')):
        #         return HttpResponseRedirect(reverse('apps.votes_results:single_option_vote', args=(poll_id,)))
            
        # check if the poll is accessed by a single poll url rather than the link with the token
        # and control of token validity
        if poll.is_votable_token():
            if request.session.get(SESSION_TOKEN_USED) is None:
                return render(request, 'polls_management/token_poll_redirect.html', {'poll': poll})
            else:
                try:
                    token_poll = request.session.get(SESSION_TOKEN_USED)
                except Exception:
                    raise Http404(f"Token associated with user {token_poll.token_user} not found.")

                if not TokenValidation.validate(token_poll) and not poll.is_votable_w_so_and_mj():
                    return render(request, 'polls_management/token_poll_redirect.html', {'poll': poll})
                
                elif poll.is_votable_w_so_and_mj():
                    # check special token case with votable mj
                    if TokenValidation.validate(token_poll):
                        return HttpResponseRedirect(reverse('apps.votes_results:single_option_vote', args=(poll_id,)))
                    elif not TokenValidation.validate_mj_special_case(token_poll):
                        return render(request, 'polls_management/token_poll_redirect.html', {'poll': poll})
                    
        elif poll.is_votable_google():
            if not request.user.is_authenticated:
                return render(request, 'global/login.html', {'poll': poll})
            elif PollTokens.objects.filter(token_user=request.user, poll_fk=poll).exists():
                google_token = PollTokens.objects.get(token_user=request.user, poll_fk=poll)
                if not TokenValidation.validate(google_token) and not poll.is_votable_w_so_and_mj():
                    return render(request, 'global/login.html', {'poll': poll})
                elif poll.is_votable_w_so_and_mj():
                    if not TokenValidation.validate(google_token):
                        if not TokenValidation.validate_mj_special_case(google_token):
                            return render(request, 'global/login.html', {'poll': poll})
            elif not PollTokens.objects.filter(token_user=request.user, poll_fk=poll).exists() and poll.is_votable_w_so_and_mj():
                return HttpResponseRedirect(reverse('apps.votes_results:single_option_vote', args=(poll_id,)))

        if ((poll.poll_type != PollModel.PollType.MAJORITY_JUDJMENT and not poll.is_votable_w_so_and_mj()) or
            ( poll.poll_type == PollModel.PollType.SINGLE_OPTION and
              request.session.get(SESSION_SINGLE_OPTION_VOTE_ID) is None and 
              not poll.is_votable_token() and not poll.is_votable_google())
            ):
            raise Http404()

        options_selected = request.session.get(SESSION_MJ_VOTE_SUBMIT_ERROR)
        if options_selected is not None:
            del request.session[SESSION_MJ_VOTE_SUBMIT_ERROR]
        
        guide_already_viwed: bool = request.session.get(SESSION_MJ_GUIDE_ALREADY_VIWED)

        if request.session.get(SESSION_MJ_GUIDE_ALREADY_VIWED) is None:
            request.session[SESSION_MJ_GUIDE_ALREADY_VIWED] = True
        
        if poll.poll_type == PollModel.PollType.SINGLE_OPTION and poll.is_votable_w_so_and_mj() and request.session.get(SESSION_SINGLE_OPTION_VOTE_ID) is not None:
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

        super().post(request, poll_id, *args, **kwargs)

        poll = self.vote_permission_checker.poll
        
        # check if there is an attempt to vote with a token already used
        if poll.is_votable_token() and request.session.get(SESSION_TOKEN_USED) is not None:
            try:
                token_poll_data = request.session.get(SESSION_TOKEN_USED)
                updated_token = PollTokenService.get_poll_token_by_user(token_poll_data.token_user)
            except Exception:
                return render(request, 'polls_management/token_poll_redirect.html', {'poll': poll})
            
            if not TokenValidation.validate(updated_token) and not TokenValidation.validate_mj_special_case(updated_token):
                return render(request, 'polls_management/token_poll_redirect.html', {'poll': poll})

        elif poll.is_votable_google():
            if PollTokens.objects.filter(token_user=request.user, poll_fk=poll).exists():
                google_token = PollTokens.objects.get(token_user=request.user, poll_fk=poll)
                if not TokenValidation.validate(google_token) and not TokenValidation.validate_mj_special_case(google_token):
                    return render(request, 'global/login.html', {'poll': poll})

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
            if poll.is_votable_token() and request.session.get(SESSION_TOKEN_USED) is not None:
                try:
                    token_poll = request.session.get(SESSION_TOKEN_USED)
                    PollTokenService.check_majority_option(token_poll)
                except Exception:
                    raise Http404(f"Token associated with user {token_poll.token_user} not found.")
            
            elif poll.is_votable_google():

                if PollTokens.objects.filter(token_user=request.user, poll_fk=poll).exists():
                    g_token = PollTokens.objects.get(token_user=request.user, poll_fk=poll)
                else:
                    PollTokenService.create_google_record(request.user, poll)
                    g_token = PollTokens.objects.get(token_user=request.user, poll_fk=poll)

                PollTokenService.check_majority_option(g_token)

            # Clear session if the mj vote is performed
            check_consistency_session.clear_session([SESSION_SINGLE_OPTION_VOTE_ID, SESSION_CONSISTENCY_CHECK])
            
        except PollOptionRatingUnvalidException:
        
            request.session[SESSION_MJ_VOTE_SUBMIT_ERROR] = session_object
            return HttpResponseRedirect(reverse('apps.votes_results:majority_judgment_vote', args=(poll_id,)))
        except Exception as e:
            raise Http404

        # Clean session data for single option to majority control
        if request.session.get('os_to_mj') is not None:
            del request.session['os_to_mj']

        # Clean eventual error session.
        if request.session.get(SESSION_MJ_VOTE_SUBMIT_ERROR) is not None:
            del request.session[SESSION_MJ_VOTE_SUBMIT_ERROR]

        # Save user vote in session
        request.session[SESSION_MJ_SUBMIT_ID] = vote.id

        # Redirect to get request.
        return HttpResponseRedirect(reverse('apps.votes_results:majority_judgment_recap', args=(poll_id, )))


