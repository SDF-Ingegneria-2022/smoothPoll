from apps.polls_management.models import PollModel

class SingleOptionVoteCounter:
    """Class to count votes for a single option poll."""
    def __init__(self, poll: PollModel):
        self._poll: PollModel = poll
        
    
    def count_single_option_votes(self) -> int:
        """Count votes for a single option poll.
            Returns:
                int: Number of votes.
        """
        pass
    
    def count_majority_judgment_votes(self):
        """Count votes for a majority judgment poll.
            Returns:
                int: Number of votes.
        """
        pass