from apps.polls_management.classes.poll_token_validation.token_validation import TokenValidation
from apps.polls_management.models.poll_token import PollTokens
from apps.polls_management.services.poll_service import PollService
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

#da modificare con 'vote'
REQUEST_VOTE = 'option_order'

SESSION_SINGLE_OPTION_VOTE_SUBMIT_ERROR = 'vote-submit-error'
SESSION_SINGLE_OPTION_VOTE_ID = 'single-option-vote-id'
SESSION_TOKEN_USED = 'token_used'


class SchulzeMethodVoteView(VoteViewSchema):
    """View to handle Single Option vote operation. """

    def get_votemethod(self) -> PollModel.PollType:
        return PollModel.PollType.SCHULZE
    
    def get_recap_page_url_name(self) -> str:
        return 'apps.votes_results:schulze_method_recap'
    
    def render_vote_form(self, request: HttpRequest) -> HttpResponse:
        return render(request, 
                    'votes_results/schulze_method_vote.html', 
                    { 
                        'poll': self.poll()
                    })
        # Get eventual error message and clean it
        """
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
        """

    def perform_vote_or_redirect_to_form(self, request: HttpRequest) -> HttpResponse:
        print(request.POST)
        
        # Check is passed any data.
        """
        if REQUEST_VOTE not in request.POST:
            request.session[SESSION_SINGLE_OPTION_VOTE_SUBMIT_ERROR] = "Errore! Per confermare la scelta " \
                + "devi esprimere una preferenza."
            return HttpResponseRedirect(reverse('apps.votes_results:schulze_method_vote', args=(self.poll().id,)))

        # Save vote preference in session
        request.session[SESSION_SINGLE_OPTION_VOTE_ID] = request.POST[REQUEST_VOTE]
        
        # Perform vote and handle missing vote or poll exception.
        try:
            vote = SingleOptionVoteService.perform_vote(
                self.poll().id, request.POST[REQUEST_VOTE])
        except PollOptionUnvalidException:
            request.session[SESSION_SINGLE_OPTION_VOTE_SUBMIT_ERROR] = "Errore! La scelte deve essere " \
                + "espressa tramite l'apposito form. Se continui a vedere questo " \
                + "messaggio contatta gli sviluppatori."
            return HttpResponseRedirect(
                reverse('apps.votes_results:single_option_vote', 
                        args=(self.poll().id,)
                ))
        except PollDoesNotExistException:
            raise Http404

        # Clean eventual error session.
        if request.session.get(SESSION_SINGLE_OPTION_VOTE_SUBMIT_ERROR) is not None:
            del request.session[SESSION_SINGLE_OPTION_VOTE_SUBMIT_ERROR]
            """
        print(request.POST.getlist('option_order'))
        # Save user vote in session (so when I re-render with GET I have the vote).
        request.session['vote-submit-id'] = request.POST.getlist('option_order')

        return None
