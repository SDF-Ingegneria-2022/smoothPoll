from apps.polls_management.exceptions.token_does_not_exist_exception import TokenDoesNotExistException

from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.models.poll_token import PollTokens
from django.core.exceptions import ObjectDoesNotExist


class NoToken:
    single_option_use = False
    majority_use = False


class TokenValidator:
    """A tool to validate a token using a sequence of steps
    """

    def __init__(self) -> None:
        self.token = NoToken()

    def load_token_from_user(self, user, poll: PollModel):

        try:
            self.token = PollTokens.objects.get(
                token_user=user, poll_fk = poll)
        except ObjectDoesNotExist:
            self.token = NoToken()

    def is_token_load(self):
        return not isinstance(self.token, NoToken)

    def is_token_valid(self): 
        return not isinstance(self.token, NoToken)
        
    def is_token_available_for_votemethod(self, votemethod: PollModel.PollType) -> bool:
        
        if votemethod == PollModel.PollType.SINGLE_OPTION:
            return not self.token.single_option_use
        
        if votemethod == PollModel.PollType.MAJORITY_JUDJMENT:
            return not self.token.majority_use
        
        return False
        
    def is_token_voted_so_but_not_mj(self) -> bool:

        if not self.is_token_load():
            return False

        return self.token.single_option_use and not self.token.majority_use
    
    def mark_votemethod_as_used(self, votemethod: PollModel.PollType):
        
        if not self.is_token_load():
            raise Exception("Cannot mark a token as used if it's not load")
        
        if votemethod == PollModel.PollType.SINGLE_OPTION:
            if self.token.single_option_use:
                raise Exception("Cannot vote two times with same method (single option)")
            
            self.token.single_option_use = True
            self.token.save()
            return

        if votemethod == PollModel.PollType.MAJORITY_JUDJMENT:
            if self.token.majority_use:
                raise Exception("Cannot vote two times with same method (majority judgment)")

            self.token.majority_use = True
            self.token.save()
            return

        raise Exception("Unvalid votemethod")

 

    




    