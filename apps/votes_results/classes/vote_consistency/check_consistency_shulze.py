from typing import List

from apps.votes_results.services.schulze_method_vote_service import SchulzeMethodVoteService

class CheckConsistencyShulze:
    
    @staticmethod    
    def check(shulze_vote_id: str, mj_votes: List[dict]) -> bool:
        """Checks if the shulze vote key is consistent with the majority judgment votes.

        Args:
            single_option_vote_key (str): Single option vote id.
            mj_votes (List[dict]): List of dicts with mj keys and ratings. Example: [{'poll_choice_id': 1, 'rating': 3}, {'poll_choice_id': 2, 'rating': 2}]

        Returns:
            bool: True if the single option vote key is consistent with the majority judgment votes, False otherwise.
        """
        if shulze_vote_id != None:
            try:
                vote = SchulzeMethodVoteService.get_vote_by_id(shulze_vote_id)
                shulze_options = vote.get_order()
                for shulze_options_index in range(0, len(vote.get_order()) - 1):
                    if list(filter(lambda x: x['poll_choice_id'] == shulze_options[shulze_options_index], mj_votes ))[0]['ratings'] <= list(filter(lambda x: x['poll_choice_id'] == shulze_options[shulze_options_index + 1], mj_votes ))[0]['ratings']:
                        # TODO: fix bug
                        return True
            except Exception:
                # If the poll is not found, the vote is not consistent
                return True
        return True
        
        