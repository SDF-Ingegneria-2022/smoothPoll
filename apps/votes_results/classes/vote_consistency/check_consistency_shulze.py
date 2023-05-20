from typing import List

from apps.votes_results.services.schulze_method_vote_service import SchulzeMethodVoteService

class CheckConsistencyShulze:
    
    @staticmethod    
    def check(shulze_vote_id: str, mj_votes: List[dict]) -> bool:
        """Checks if the shulze vote key is consistent with the majority judgment votes.

        Args:
            shulze_vote_id (str): Shulze vote option vote id.
            mj_votes (List[dict]): List of dicts with mj keys and ratings. Example: [{'poll_choice_id': 1, 'rating': 3}, {'poll_choice_id': 2, 'rating': 2}]

        Returns:
            bool: True if the Shulze option vote key is consistent with the majority judgment votes, False otherwise.
        """
        if shulze_vote_id != None:
            try:
                vote = SchulzeMethodVoteService.get_vote_by_id(shulze_vote_id)
                shulze_options: list = vote.get_order()
                
                for shulze_options_index in range(0, len(vote.get_order()) - 1):
                    previous_rating: list= list(filter(lambda x: x['poll_choice_id'] == int(shulze_options[shulze_options_index]), mj_votes ))[0]['rating']
                    next_rating: list = list(filter(lambda x: x['poll_choice_id'] == int(shulze_options[shulze_options_index + 1]), mj_votes ))[0]['rating']
                    
                    if previous_rating < next_rating:
                        return False
            except Exception as e:
                # If the poll is not found, the vote is not consistent
                return False
        return True
        
        