
from typing import List
from django.urls import reverse
from django.utils.crypto import get_random_string
from sesame.utils import get_query_string
from django.contrib.auth.models import User
from apps.polls_management.exceptions.token_does_not_exist_exception import TokenDoesNotExistException
from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.models.poll_token import PollTokens
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

class PollTokenService:

    """Service class for poll tokens management"""

    @staticmethod
    def create_tokens(token_number: int, poll: PollModel) -> List[PollTokens]:

        """Create tokens for the poll and store them in the database.
        Args:
            token_number: number of tokens to create.
            poll: poll to assign tokens created.
        Returns:
            tokens: list of tokens created.
        """

        tokens: List[PollTokens] = []

        # creation of a token link for as many times as dictated
        for x in range(token_number):

            # creation of a phantom user to assign a token and database integrity control
            # (if a user with the same name already exists)
            unique_id = get_random_string(length=8)
            while (User.objects.filter(username=unique_id).exists()):
                unique_id = get_random_string(length=8)

            phantomuser: User = User.objects.create_user(username=unique_id)
  
            # creation of database table for new token
            new_token: PollTokens = PollTokens(token_user=phantomuser, poll_fk=poll)
            new_token.save()
            
            tokens.append(new_token)

        return tokens
    
    @staticmethod
    def get_poll_token_by_user(user: User) -> PollTokens:

        """Get a poll token by its user.
        Args:
            user: user whom the token is assigned to.
        Raises:
            TokenDoesNotExistException: raised when you retrieve a non-existent token.
        Returns:
            poll_token: token associated with the user.
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
        Returns:
            Bool indicating if token is used for a single option poll or not.
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
        Returns:
            Bool indicating if token is used for a majority judgment poll or not.
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

    @staticmethod
    def available_token_list(poll: PollModel) -> List[PollTokens]:

        """Return a list of available tokens.
        Args:
            poll: the poll the tokens belong to.
        Returns:
            List of available token links.
        """

        return PollTokens.objects.filter(
                Q(poll_fk=poll) & Q(single_option_use=False) 
                & Q(majority_use=False)
            ).order_by('-created_at').all()

    def delete_tokens(poll: PollModel):

        """Delete tokens and related phantom users for the specified list.
        Args:
            poll: the poll the tokens belong to.
        """

        # get all tokens for the specified poll, be them available or not
        tokens: PollTokens = PollTokens.objects.filter(poll_fk=poll)

        # if there are tokens for the poll, delete the phantom users and then their tokens
        if tokens:
            for token in tokens:
                phantouser: User = token.token_user
                phantouser.delete()
                token.delete()

    @staticmethod
    def unavailable_token_list(poll: PollModel) -> List[PollTokens]:

        """Return a list of unavailable token links.
        Args:
            poll: the poll the tokens belong to.
        Returns:
            List of unavailable token links.
        """

        return PollTokens.objects.filter(Q(poll_fk=poll) & Q(Q(single_option_use=True) | Q(majority_use=True))).all()
    
    @staticmethod
    def create_google_record(user: User, poll: PollModel) -> PollTokens:

        """Creates an object PollTokens used to record a vote for a Google auth user.
        Args:
            user: the user whose vote has to be recorded.
            poll: the poll the tokens belong to.
        Returns:
            google_vote: the token representing the user's vote with Google email.
        """

        google_vote: PollTokens = PollTokens(token_user=user, poll_fk=poll)
        google_vote.save()

        return google_vote
    
    
