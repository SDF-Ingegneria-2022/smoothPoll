from polls.classes.vote_factory import VoteFactory
from polls.models.vote_model import VoteModel
from polls.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
from polls.exceptions.poll_option_unvalid_exception import PollOptionUnvalidException
from django.core.exceptions import ObjectDoesNotExist

class VoteService: 
    """
    Handle vote procedures 
    """

    @staticmethod
    def perform_vote(poll_id: str, poll_choice_id: str) -> VoteModel:
        """
        Perform a vote on a survey.
        """

        vote = VoteFactory.create_vote(poll_id, poll_choice_id)
        vote.save()
        
        return vote
