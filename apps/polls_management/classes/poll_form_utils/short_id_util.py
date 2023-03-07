
from typing import List
from apps.polls_management.models.poll_model import PollModel
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