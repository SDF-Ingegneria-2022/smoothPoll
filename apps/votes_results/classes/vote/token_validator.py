import abc
from apps.polls_management.exceptions.poll_does_not_exist_exception import PollDoesNotExistException

from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.models.poll_token import PollTokens
from apps.polls_management.services.poll_token_service import PollTokenService


class TokenValidator(abc.ABC):
    """A tool to validate a token using a sequence of steps
    """


    def load_token_from_user(self, user) -> bool:

        if user is None:
            return False

        try:
            self.token: PollTokens = \
                PollTokenService.get_poll_token_by_user(user)
        except PollDoesNotExistException:
            return False
        
        return True


    def is_token_related_to_poll(self, poll: PollModel) -> bool:
        return self.token.poll_fk == poll
    
    def is_token_available_for_votemethod(self, votemethod: PollModel.PollType) -> bool:
        
        if votemethod == PollModel.PollType.SINGLE_OPTION:
            return not self.token.single_option_use
        
        if votemethod == PollModel.PollType.MAJORITY_JUDJMENT:
            return not self.token.majority_use
        
        return False
        
    def is_token_voted_so_but_not_mj(self) -> bool:
        return self.token.single_option_use and not self.token.majority_use
 

    




    