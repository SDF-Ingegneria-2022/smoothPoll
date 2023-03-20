from typing import List
from apps.polls_management.models.poll_model import PollModel


class CheckConsistencyMjVote:
    
    @staticmethod    
    def check(single_option_vote_key: str, mj_votes: List[dict]) -> bool:
        max_rating: dict = [max(mj_votes, key=lambda x:x['rating'])]
        items_with_max_rating: List[dict] = [item for item in mj_votes if item['rating'] == max_rating[0]['rating']]
        # Check if the key is in the list of max ratings
        if not any(item['poll_choice_id'] == single_option_vote_key for item in items_with_max_rating):
            return True
        
        return False
     