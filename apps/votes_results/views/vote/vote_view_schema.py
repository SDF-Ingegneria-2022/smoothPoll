import abc
from django.http import Http404

from django.views import View

from apps.votes_results.classes.vote.vote_permissions_checker import VotePermissionsChecker


class VoteViewSchema(abc.ABC, View):
    """
    Abstract schema for a vote view. 

    It implements (on high level) the management of get and post requests, 
    using a VotePermissionsChecker + some template methods.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # init tool to make all needed checks
        # to ensure poll is votable (by this user)
        self.vote_permission_checker = VotePermissionsChecker()

    
    def get(self, request, poll_id, *args, **kwargs):
        if not self.vote_permission_checker.load_poll(poll_id):
            raise Http404(f"Poll with id {poll_id} not found.")
        
        return None

    def post(self, request, poll_id, *args, **kwargs):
        if not self.vote_permission_checker.load_poll(poll_id):
            raise Http404(f"Poll with id {poll_id} not found.")
        
        return None