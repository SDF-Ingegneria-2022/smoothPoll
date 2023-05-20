from apps.polls_management.models import PollModel
from apps.polls_management.models.majority_vote_model import MajorityVoteModel
from apps.votes_results.exceptions.not_single_option_poll_exception import NotSingleOptionPollException

class MjVoteCounter:
    """Class to count votes for a single option poll."""
    def __init__(self, poll: PollModel):
        self._poll: PollModel = poll
    
    def count_majority_judgment_votes(self):
        """Count votes for a majority judgment poll.
            Returns:
                int: Number of votes.
        """
        
        votes: MajorityVoteModel = MajorityVoteModel.objects.filter(poll=self._poll.id)
        
        return len(votes)