import abc

from django.http import HttpRequest

from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.models.poll_token import PollTokens
from apps.votes_results.classes.vote.token_validator import TokenValidator


class IsUserAllowedChecker(abc.ABC): 

    @abc.abstractmethod
    def is_user_allowed(self): 
        pass

    @abc.abstractmethod
    def is_user_allowed_for_votemethod(self, votemethod: PollModel.PollType): 
        pass

    @abc.abstractmethod
    def is_voted_so_but_not_mj(self):
        pass

class NoAuthChecker(IsUserAllowedChecker):

    def is_user_allowed(self): 
        return True

    def is_user_allowed_for_votemethod(self, votemethod: PollModel.PollType): 
        return True

    def is_voted_so_but_not_mj(self):
        return False
    
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
        
        if self._checker.token_validator.token == None:
            return True
        
        return self._checker.is_user_allowed_for_votemethod(votemethod)

    def is_voted_so_but_not_mj(self):
        return self._checker.is_voted_so_but_not_mj()
    

def is_user_allowed_factory(request: HttpRequest, poll: PollModel) -> IsUserAllowedChecker:
    
    if poll.is_votable_token():
        token = request.session.get('token_used')
        user = None if token is None else token.token_user
        return TokenChecker(user, poll)
    
    if poll.is_votable_google():
        return GoogleChecker(request.user, poll)
    
    return NoAuthChecker()