from typing import List
from apps.polls_management.models.poll_model import PollModel


class CheckConsistencyMjVote:
    
    @staticmethod    
    def check(single_option_vote_key: str, mj_votes: List[dict]) -> bool:
        """Checks if the single option vote key is consistent with the majority judgment votes.

        Args:
            single_option_vote_key (str): Single option vote id.
            mj_votes (List[dict]): List of dicts with mj keys and ratings. Example: [{'poll_choice_id': 1, 'rating': 3}, {'poll_choice_id': 2, 'rating': 2}]

        Returns:
            bool: True if the single option vote key is consistent with the majority judgment votes, False otherwise.
        """
        max_rating: dict = [max(mj_votes, key=lambda x:x['rating'])]
        items_with_max_rating: List[dict] = [item for item in mj_votes if item['rating'] == max_rating[0]['rating']]
        
        for item in items_with_max_rating:
            if item['poll_choice_id'] == int(single_option_vote_key):
                return True
        return False
     