from apps.polls_management.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.services.poll_service import PollService


class VotePermissionsChecker:
    """
    A class (inspired to the Strategy pattern 
    - https://refactoring.guru/design-patterns/strategy -
    but less complicate) that contains all the "permission checks"
    you have to do before submitting a vote or rendering the
    vote page.

    Each method, returns True if the check is passed, False otherwise.
    """

    poll: PollModel = None

    def load_poll(self, poll_id) -> bool:
        """Load the poll with the given id (ensure it exists)"""

        if poll_id is None:
            return False
        
        try:
            self.poll = PollService.get_poll_by_id(poll_id)
            return True
        except PollDoesNotExistException:
            return False
        
    def is_poll_votable(self) -> bool:
        """Check if the poll is votable"""
        return self.poll.is_open() and not self.poll.is_closed()
