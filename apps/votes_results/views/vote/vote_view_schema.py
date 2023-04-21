import abc
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from django.views import View
from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.models.poll_token import PollTokens

from apps.votes_results.classes.vote.is_poll_votable_checker import IsPollVotableChecker
from apps.votes_results.classes.vote.token_validator import TokenValidator


class VoteViewSchema(abc.ABC, View):
    """
    Abstract schema for a vote view. 

    It implements (on high level) the management of get and post requests, 
    using a VotePermissionsChecker + some template methods.
    """

    @abc.abstractmethod
    def get_votemethod(self) -> PollModel.PollType:
        pass

    def poll(self) -> PollModel:
        return self.poll_votable_checker.poll
    
    def token(self) -> PollTokens:
        return self.token_validator.token

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # init tool to check poll is votable (now)
        self.poll_votable_checker = IsPollVotableChecker()

        # init tool to validate eventual token
        self.token_validator = TokenValidator()

    # def dispatch(self, request, poll_id, *args, **kwargs):
    #     return super().dispatch(request, poll_id, *args, **kwargs)

    
    def get(self, request, poll_id, *args, **kwargs):
        
        # check poll exists
        if not self.poll_votable_checker.load_poll(poll_id):
            raise Http404(f"Poll with id {poll_id} not found.")
        
        # check if poll is votable through this vote method 
        if not self.poll_votable_checker\
            .is_poll_votable_through_method(self.get_votemethod()):
            raise Http404(f"Poll with id {poll_id} is not votable through this vote method.")
        
        # check poll is open (votable now)
        if not self.poll_votable_checker.is_poll_open_for_votes():
            return render(
                request, 
                'votes_results/poll_details.html', 
                {'poll': self.poll_votable_checker.poll}
                )
        
        if self.poll().is_votable_token():
            # TODO: replace with just user
            token = request.session.get('token_used')

            # check token is 1) valid, 2) related to this poll 
            if token is None or \
                not self.token_validator.load_token_from_user(token.token_user) or \
                not self.token_validator.is_token_related_to_poll(self.poll()):

                return render(
                    request, 
                    'polls_management/token_poll_redirect.html', 
                    {'poll': self.poll(), })
            
            # check token is 3) available for this method 
            # (+ handle special SO + MJ case)
            if not self.token_validator.is_token_available_for_votemethod(self.get_votemethod()):
                return render(
                    request, 
                    'polls_management/token_poll_redirect.html', 
                    {
                        'poll': self.poll(), 
                        'mj_not_used': self.poll().is_votable_w_so_and_mj() and \
                            self.token_validator.is_token_voted_so_but_not_mj() 
                    })

        return None

    def post(self, request, poll_id, *args, **kwargs):

        # check poll exists
        if not self.poll_votable_checker.load_poll(poll_id):
            raise Http404(f"Poll with id {poll_id} not found.")
        
        # check if poll is votable through this vote method 
        if not self.poll_votable_checker\
            .is_poll_votable_through_method(self.get_votemethod()):
            raise Http404(f"Poll with id {poll_id} is not votable through this vote method.")
        
        # check poll is open (votable now)
        if not self.poll_votable_checker.is_poll_open_for_votes():
            return HttpResponseRedirect(reverse(
                'apps.polls_management:poll_details', 
                args=(poll_id,)
                ))
        
        if self.poll().is_votable_token():
            # TODO: replace with just user
            # TODO: move constant here
            token = request.session.get('token_used')

            # check token is 1) valid, 2) related to this poll, 
            # 3) available for this method 
            if token is None or \
                not self.token_validator.load_token_from_user(token.token_user) or \
                not self.token_validator.is_token_related_to_poll(self.poll()) or \
                not self.token_validator.is_token_available_for_votemethod(self.get_votemethod()):
                
                # no special case handling, control on POST is more a security
                # check than a thing that should help the user
                return render(
                    request, 
                    'polls_management/token_poll_redirect.html', 
                    {'poll': self.poll(), })
        
        return None