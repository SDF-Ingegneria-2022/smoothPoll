from django.db.models import Q
from typing import List
from apps.polls_management.models.poll_model import SHORT_ID, PollModel
import random
import string

class ShortIdUtil:

    @staticmethod
    def generate() -> str:
        """Generate a short id for a poll that is unique in the db
            Returns:
                str: Unique short id.
        """
        short_ids: List[str] = list(PollModel.objects.values_list('short_id', flat=True))
        new_id: str = ''.join(random.choice(string.ascii_lowercase) for i in range(6))
        
        limit: int = 100
        while new_id in short_ids and limit > 0:
            new_id = ''.join(random.choice(string.ascii_lowercase) for i in range(6))
            limit -= 1
        
        if limit == 0:
            raise Exception("Error generating short id")

        return new_id
    
    @staticmethod
    def validate(short_id: str) -> bool:
        """Validate the short id.
        
        Args:
            short_id (str): Short id to validate.
        
        Returns:
            bool: True if the short id is valid, False otherwise.
        """
        short_ids: List[str] = list(PollModel.objects.values_list('short_id', flat=True))
        if len(short_id) == 6 and short_id not in short_ids:
            return True
        else:
            return False
        
    def __init__(self, code: str, poll: PollModel=None) -> None:
        self.code: str = code or ""
        self.poll: PollModel = poll
        
    def validate_length(self) -> bool:
        return len(self.code) >= 6 and len(self.code) <= 60
    
    def validate_characters(self) -> bool:
        return self.code.isalnum()
    
    def validate_uniqness(self) -> bool:

        query = PollModel.objects.filter(short_id=self.code)

        # if I am working on an already existent poll is acceptable
        # this code is already used for this poll
        if not self.poll is None:
            query = query.filter(~Q(id__in=[self.poll.id]))

        return query.count() == 0
        
    