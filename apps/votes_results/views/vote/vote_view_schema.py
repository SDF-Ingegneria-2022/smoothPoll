import abc
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from django.views import View
from apps.polls_management.models.poll_model import PollModel

from apps.votes_results.classes.vote.vote_permissions_checker import VotePermissionsChecker


class VoteViewSchema(abc.ABC, View):
    """
    Abstract schema for a vote view. 

    It implements (on high level) the management of get and post requests, 
    using a VotePermissionsChecker + some template methods.
    """

    @abc.abstractmethod
    def get_votemethod(self) -> PollModel.PollType:
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # init tool to make all needed checks
        # to ensure poll is votable (by this user)
        self.vote_permission_checker = VotePermissionsChecker()

    # def dispatch(self, request, poll_id, *args, **kwargs):
    #     return super().dispatch(request, poll_id, *args, **kwargs)

    
    def get(self, request, poll_id, *args, **kwargs):
        
        # check poll exists
        if not self.vote_permission_checker.load_poll(poll_id):
            raise Http404(f"Poll with id {poll_id} not found.")
        
        # check if poll is votable through this vote method 
        if not self.vote_permission_checker\
            .is_poll_votable_through_method(self.get_votemethod()):
            raise Http404(f"Poll with id {poll_id} is not votable through this vote method.")
        
        # check poll is open (votable now)
        if not self.vote_permission_checker.is_poll_open_for_votes():
            return render(
                request, 
                'votes_results/poll_details.html', 
                {'poll': self.vote_permission_checker.poll}
                )
        

        return None

    def post(self, request, poll_id, *args, **kwargs):

        # check poll exists
        if not self.vote_permission_checker.load_poll(poll_id):
            raise Http404(f"Poll with id {poll_id} not found.")
        
        # check if poll is votable through this vote method 
        if not self.vote_permission_checker\
            .is_poll_votable_through_method(self.get_votemethod()):
            raise Http404(f"Poll with id {poll_id} is not votable through this vote method.")
        
        # check poll is open (votable now)
        if not self.vote_permission_checker.is_poll_open_for_votes():
            return HttpResponseRedirect(reverse(
                'apps.polls_management:poll_details', 
                args=(poll_id,)
                ))
        
        return None