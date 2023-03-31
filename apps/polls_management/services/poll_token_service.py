
from typing import List
from django.utils.crypto import get_random_string
from sesame.utils import get_query_string
from django.contrib.auth.models import User
from apps.polls_management.exceptions.token_does_not_exist_exception import TokenDoesNotExistException
from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.models.poll_token import PollTokens
from django.core.exceptions import ObjectDoesNotExist

class PollTokenService:

    """Service class for poll tokens management"""

    @staticmethod
    def create_tokens(link: str, token_number: int, poll: PollModel) -> List[str]:

        """Method used to create and store tokens in an object on database"""

        token_links: List[str] = []
        templink: str = []

        # creation of a token link for as many times as dictated
        for x in range(token_number):

            # creation of a phantom user to assign a token and database integrity control
            # (if a user with the same name already exists)
            unique_id = get_random_string(length=8)
            while (User.objects.filter(username=unique_id).exists()):
                unique_id = get_random_string(length=8)

            phantomuser: User = User.objects.create_user(username=unique_id)
            templink = link
            templink += get_query_string(user=phantomuser, scope=f"Poll:{poll.id}")

            # creation of database table for new token
            new_token: PollTokens = PollTokens(token_user=phantomuser, poll_fk=poll)
            new_token.save()
            
            token_links.append(templink)

        return token_links
    
    @staticmethod
    def get_poll_token_by_user(user: User) -> PollTokens:

        """Get a poll token by its user.
        Args:
            user: user whom the token is assigned to.
        Raises:
            TokenDoesNotExistException: raised when you retrieve a non-existent token.
        """

        try:
            poll_token: PollTokens = PollTokens.objects.get(token_user=user)
        except ObjectDoesNotExist:
            raise TokenDoesNotExistException(f"Error: token with user={user} does not exit")    
        
        return poll_token
    
    @staticmethod
    def is_single_option_token_used(token: PollTokens) -> bool:

        """Check if a token is used for a single option poll.
        Args:
            token: token model with all necessary information.
        """

        if token.single_option_use:
            return True
        else:
            return False

    @staticmethod
    def is_majority_token_used(token: PollTokens) -> bool:

        """Check if a token is used for a majority poll.
        Args:
            token: token model with all necessary information.
        """

        if token.majority_use:
            return True
        else:
            return False

    @staticmethod
    def check_single_option(token: PollTokens):

        """Make token for single option as already used.
        Args:
            token: token model with all necessary information.
        """

        token.single_option_use = True
        token.save()

    @staticmethod
    def check_majority_option(token: PollTokens):

        """Make token for majority option as already used.
        Args:
            token: token model with all necessary information.
        """

        token.majority_use = True
        token.save()