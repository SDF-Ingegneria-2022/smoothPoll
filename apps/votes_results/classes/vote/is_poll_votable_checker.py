from apps.polls_management.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.services.poll_service import PollService


class IsPollVotableChecker:
    """
    A class  that contains all the checks to ensure a poll is votable now.

    Each method, makes a check and returns True if the check is passed, False otherwise.
    """

    poll: PollModel = None

    def load_poll(self, poll_id) -> bool:
        """Load the poll with the given id (ensure it exists)"""

        if poll_id is None:
            return False
        
        try:
            self.poll: PollModel = PollService.get_poll_by_id(poll_id)
            return True
        except PollDoesNotExistException:
            return False
        
    def is_poll_open_for_votes(self) -> bool:
        """Check if curr date is in the dates interval where poll is open for vote"""
        return self.poll.is_open() and not self.poll.is_closed()
    
    def is_poll_votable_through_method(self, votemethod: PollModel.PollType) -> bool:
        """Check if the poll is votable through the given method"""
        
        if self.poll.poll_type == votemethod:
            return True # same vote method --> OK
        
        # else I check the special case "votable also w MJ"
        return self.poll.is_votable_w_so_and_mj()