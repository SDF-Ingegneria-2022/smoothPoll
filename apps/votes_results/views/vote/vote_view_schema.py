import abc
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from django.views import View
from apps.polls_management.models.poll_model import PollModel

from apps.votes_results.classes.vote.is_poll_votable_checker import IsPollVotableChecker
from apps.votes_results.classes.vote.is_user_allowed_checker import is_user_allowed_factory


class VoteViewSchema(abc.ABC, View):
    """
    Abstract schema for a vote view. 

    It implements (on high level) the management of get and post requests, 
    using a VotePermissionsChecker + some template methods.
    """

    @abc.abstractmethod
    def get_votemethod(self) -> PollModel.PollType:
        """Get the votemethod user is using"""
        pass
    
    @abc.abstractmethod
    def render_vote_form(self, request: HttpRequest) -> HttpResponse:
        """Render the form user will use to vote"""
        pass
    
    @abc.abstractmethod
    def perform_vote_or_redirect_to_form(self, request: HttpRequest) -> HttpResponse:
        """Perform a vote or redirect to vote form if it fails.
            :Return None if everything is okay, else the redirect
        """
        pass 
    
    @abc.abstractmethod
    def get_recap_page_url_name(self) -> str:
        """The django name of the url where I will render vote recap"""
        pass

    def poll(self) -> PollModel:
        """Current poll object"""
        return self.poll_votable_checker.poll
    
    def nonauth_user_template_name(self) -> str:
        """Name of template to display if user is not 
        authorized to perform a vote"""

        if self.poll().is_votable_google():
            return 'global/login.html'
        
        return 'polls_management/token_poll_redirect.html'
    
    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # init tool to check poll is votable (now)
        self.poll_votable_checker = IsPollVotableChecker()

        # tool to check if user is allowed to vote
        self.is_user_allowed_checker = None
    
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
        
        # init checker with appropriate votemethod
        self.is_user_allowed_checker = is_user_allowed_factory(request, self.poll())

        # check user is generally allowed to access this poll 
        if not self.is_user_allowed_checker.is_user_allowed():
            return render(
                request, 
                self.nonauth_user_template_name(), 
                {'poll': self.poll(), })
        
        # check user is allowed to use specifically this votemethod
        if not self.is_user_allowed_checker.is_user_allowed_for_votemethod(self.get_votemethod()):
            return render(
                request, 
                self.nonauth_user_template_name(), 
                {
                    'poll': self.poll(), 
                    'mj_not_used': self.poll().is_votable_w_so_and_mj() and \
                        self.is_user_allowed_checker.is_voted_so_but_not_mj() 
                })
        
        # render vote form (or other response)
        return self.render_vote_form(request)

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
        
        # init checker with appropriate votemethod
        self.is_user_allowed_checker = is_user_allowed_factory(request, self.poll())

        # check user is allowed to submit this vote
        if not self.is_user_allowed_checker.is_user_allowed() or \
            not self.is_user_allowed_checker.is_user_allowed_for_votemethod(
            self.get_votemethod()):

            return render(
                request, 
                self.nonauth_user_template_name(), 
                {'poll': self.poll(), })
                
        # submit vote (or return error if something got wrong)
        res = self.perform_vote_or_redirect_to_form(request)
        if not res is None:
            return res
        
        # mark poll as "voted" for a certain votemethod
        self.is_user_allowed_checker.mark_votemethod_as_used(
            self.get_votemethod())

        # redirect to recap page
        return HttpResponseRedirect(reverse(
            self.get_recap_page_url_name(), args=(poll_id, )
            ))




