
from typing import List
from django.utils.crypto import get_random_string
from sesame.utils import get_query_string
from django.contrib.auth.models import User

class PollTokenService:

    """Service class for poll tokens management"""

    @staticmethod
    def create_tokens(link: str, token_number: int) -> List[str]:

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
            templink += get_query_string(user=phantomuser)

            print(templink)
            
            token_links.append(templink)

        return token_links
