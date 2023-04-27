import abc

from django.http import HttpRequest

from apps.polls_management.models.poll_model import PollModel
from apps.votes_results.classes.vote.token_validator import NoToken, TokenValidator
from apps.polls_management.services.poll_token_service import PollTokenService


class IsUserAllowedChecker(abc.ABC): 

    @abc.abstractmethod
    def is_user_allowed(self) -> bool: 
        """Check current user is allowed to access the poll"""
        pass

    @abc.abstractmethod
    def is_user_allowed_for_votemethod(self, votemethod: PollModel.PollType) -> bool: 
        """Check current user is allowed to submit 
        a vote with a certain votemethod"""
        pass

    @abc.abstractmethod
    def is_voted_so_but_not_mj(self) -> bool:
        """Check a poll is voted (by this user) w
        SO but not with MJ. It is used to handle 
        the special double vote case."""
        pass
    
    @abc.abstractmethod
    def mark_votemethod_as_used(self, votemethod: PollModel.PollType) -> None:
        """Save that a certain votemethod has been used 
        for current user/token."""
        pass 

class NoAuthChecker(IsUserAllowedChecker):

    def is_user_allowed(self): 
        return True

    def is_user_allowed_for_votemethod(self, votemethod: PollModel.PollType): 
        return True

    def is_voted_so_but_not_mj(self):
        return False
    
    def mark_votemethod_as_used(self, votemethod: PollModel.PollType):
        pass
    
class TokenChecker(IsUserAllowedChecker):

    def __init__(self, user, poll: PollModel):
        self.user = user
        self.poll = poll
        self.token_validator = TokenValidator()

    def is_user_allowed(self): 

        if self.user is None or self.user.is_anonymous:
            return False

        self.token_validator.load_token_from_user(self.user, self.poll)

        return self.token_validator.is_token_valid()

    def is_user_allowed_for_votemethod(self, votemethod: PollModel.PollType): 
        return self.token_validator.is_token_available_for_votemethod(votemethod)

    def is_voted_so_but_not_mj(self):
        return self.token_validator.is_token_voted_so_but_not_mj()
    
    def mark_votemethod_as_used(self, votemethod: PollModel.PollType):
        self.token_validator.mark_votemethod_as_used(votemethod)

    
class GoogleChecker(IsUserAllowedChecker):

    def __init__(self, user, poll: PollModel) -> None:
        self._checker = TokenChecker(user, poll)

    def is_user_allowed(self): 

        if self._checker.user is None or \
            self._checker.user.is_anonymous:
            return False
        
        self._checker.token_validator.load_token_from_user(
            self._checker.user, self._checker.poll)
        
        return True

    def is_user_allowed_for_votemethod(self, votemethod: PollModel.PollType): 
        
        if self._checker.token_validator.is_token_load() and \
            self._checker.user is None or \
            self._checker.user.is_anonymous:
            return True
        
        return self._checker.is_user_allowed_for_votemethod(votemethod)

    def is_voted_so_but_not_mj(self):
        return self._checker.is_voted_so_but_not_mj()
    
    def mark_votemethod_as_used(self, votemethod: PollModel.PollType):
        
        # if token does not exist, I create it now 
        if not self._checker.token_validator.is_token_load():

            token = PollTokenService.create_google_record(
                self._checker.user, self._checker.poll)
            self._checker.token_validator.token = token

        self._checker.mark_votemethod_as_used(votemethod)
    

def is_user_allowed_factory(request: HttpRequest, poll: PollModel) -> IsUserAllowedChecker:
    
    if poll.is_votable_token():
        token = request.session.get('token_used')
        user = None if token is None else token.token_user
        return TokenChecker(user, poll)
    
    if poll.is_votable_google():
        return GoogleChecker(request.user, poll)
    
    return NoAuthChecker()