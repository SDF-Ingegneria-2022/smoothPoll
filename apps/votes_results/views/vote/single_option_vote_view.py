from apps.polls_management.classes.poll_token_validation.token_validation import TokenValidation
from apps.polls_management.models.poll_token import PollTokens
from apps.polls_management.services.poll_token_service import PollTokenService
from apps.polls_management.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
from apps.polls_management.models.poll_model import PollModel
from apps.votes_results.exceptions.poll_option_unvalid_exception import PollOptionUnvalidException
from apps.votes_results.classes.single_option_vote_counter import SingleOptionVoteCounter
from apps.votes_results.services.single_option_vote_service import SingleOptionVoteService

from django.http import Http404, HttpResponse  
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from apps.votes_results.views.vote.vote_view_schema import VoteViewSchema


REQUEST_VOTE = 'vote'

SESSION_SINGLE_OPTION_VOTE_SUBMIT_ERROR = 'vote-submit-error'
SESSION_SINGLE_OPTION_VOTE_ID = 'single-option-vote-id'
SESSION_TOKEN_USED = 'token_used'

class SingleOptionVoteView(VoteViewSchema):
    """View to handle Single Option vote operation. """

    def get_votemethod(self) -> PollModel.PollType:
        return PollModel.PollType.SINGLE_OPTION
    
    def render_vote_form(self, request: HttpRequest) -> HttpResponse:

        if self.poll().poll_type == PollModel.PollType.MAJORITY_JUDJMENT:
            return HttpResponseRedirect(reverse('apps.votes_results:majority_judgment_vote', args=(poll_id,)))

        # Get eventual error message and clean it
        eventual_error = request.session.get(SESSION_SINGLE_OPTION_VOTE_SUBMIT_ERROR)
        if eventual_error is not None:
            del request.session[SESSION_SINGLE_OPTION_VOTE_SUBMIT_ERROR]
        
        # Render vote form (with eventual error message)
        return render(request, 
                    'votes_results/single_option_vote.html', 
                    { 
                        'poll': self.poll(), 
                        'error': eventual_error 
                    })

    # def get(self, request: HttpRequest, poll_id: int, *args, **kwargs):
    #     """Render the form wich permits user to vote"""

    #     res = super().get(request, poll_id, *args, **kwargs)
    #     if res is not None:
    #         return res

        
    def post(self, request: HttpRequest, poll_id: int, *args, **kwargs):
        """Handle vote perform and redirect to recap (or 
        redirect to form w errors)"""

        res = super().post(request, poll_id, *args, **kwargs)
        if res is not None:
            return res

        poll = self.poll()

        # Check is passed any data.
        if REQUEST_VOTE not in request.POST:
            request.session[SESSION_SINGLE_OPTION_VOTE_SUBMIT_ERROR] = "Errore! Per confermare la scelta " \
                + "devi esprimere una preferenza."
            return HttpResponseRedirect(reverse('apps.votes_results:single_option_vote', args=(poll_id,)))

        # Save vote preference in session
        request.session[SESSION_SINGLE_OPTION_VOTE_ID] = request.POST[REQUEST_VOTE]
        
        # Perform vote and handle missing vote or poll exception.
        try:
            vote = SingleOptionVoteService.perform_vote(poll_id, request.POST[REQUEST_VOTE])

            # invalidation of token if vote is successful
            self.is_user_allowed_checker.mark_votemethod_as_used(self.get_votemethod())

        except PollOptionUnvalidException:
            request.session[SESSION_SINGLE_OPTION_VOTE_SUBMIT_ERROR] = "Errore! La scelte deve essere " \
                + "espressa tramite l'apposito form. Se continui a vedere questo " \
                + "messaggio contatta gli sviluppatori."
            return HttpResponseRedirect(reverse('apps.votes_results:single_option_vote', args=(poll_id,)))
        except PollDoesNotExistException:
            raise Http404

        # Clean eventual error session.
        if request.session.get(SESSION_SINGLE_OPTION_VOTE_SUBMIT_ERROR) is not None:
            del request.session[SESSION_SINGLE_OPTION_VOTE_SUBMIT_ERROR]

        # Save user vote in session (so when I re-render with GET I have the vote).
        request.session['vote-submit-id'] = vote.id

        # RE-direct to get request.
        return HttpResponseRedirect(reverse('apps.votes_results:single_option_recap', args=(poll_id, ))) 

    
