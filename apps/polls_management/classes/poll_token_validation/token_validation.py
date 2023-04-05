
from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.models.poll_token import PollTokens
from apps.polls_management.services.poll_token_service import PollTokenService

class TokenValidation:

    """Class used to validate tokens"""

    @staticmethod
    def validate(poll: PollModel, token: PollTokens) -> bool:

        """Validate token if poll is not also votable with mj"""

        # token validation controls
        if not PollTokenService.is_single_option_token_used(token) and poll.poll_type == PollModel.PollType.SINGLE_OPTION and not poll.votable_mj:
            return True
        elif not PollTokenService.is_majority_token_used(token) and poll.poll_type == PollModel.PollType.MAJORITY_JUDJMENT and not poll.votable_mj:
            return True
        elif PollTokenService.is_single_option_token_used(token) and poll.poll_type == PollModel.PollType.SINGLE_OPTION and not poll.votable_mj:
            return False
        elif PollTokenService.is_majority_token_used(token) and poll.poll_type == PollModel.PollType.MAJORITY_JUDJMENT and not poll.votable_mj:
            return False
        elif not PollTokenService.is_single_option_token_used(token) and poll.poll_type == PollModel.PollType.SINGLE_OPTION and not PollTokenService.is_majority_token_used(token) and poll.votable_mj:
            return True
        else:
            return False
        
    @staticmethod
    def validate_mj_special_case(poll: PollModel, token: PollTokens) -> bool:

        """Validate token if poll is also votable with mj"""

        # token validation controls
        if PollTokenService.is_single_option_token_used(token) and not PollTokenService.is_majority_token_used(token) and poll.poll_type == PollModel.PollType.SINGLE_OPTION and poll.votable_mj:
            return True
        else:
            return False