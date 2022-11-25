from polls.models.vote_model import VoteModel
from polls.models.poll_model import PollModel
from polls.models.poll_option_model import PollOptionModel
from polls.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
from polls.exceptions.poll_option_unvalid_exception import PollOptionUnvalidException

from django.core.exceptions import ObjectDoesNotExist


class VoteBuilder:
    """
    A tool that will help you building a VoteModel instance. 

    To use it:
    - create an instance
    - use method set_poll(poll_id) to set the poll you want to vote
    - use method set_poll_option(poll_option_id) to set voted option
    - use perform_creation to confirm your choice and generate the model
      (call it just once)

    At end of process object is not saved.
    """

    def __init__(self) -> None:
        self.__voted_option = None
        self.__poll = None
        self.__vote_model = None
        

    def set_poll(self, poll_id: str) -> "PollVoteBuilder":
        
        self.__voted_option = None
        
        try:
            self.__poll: PollModel = PollModel.objects.get(id=poll_id)
            # todo: add here "is open" filter
        except ObjectDoesNotExist:
            raise PollDoesNotExistException(f"Error: Poll with id={poll_id} does not exist")

        return self

    def set_voted_option(self, poll_option_id: str) -> "PollVoteBuilder":
        
        try:
            self.__voted_option: PollOptionModel = PollOptionModel.objects \
                .filter(poll_fk=self.__poll.id) \
                .get(id=poll_option_id)

        except ObjectDoesNotExist:
            raise PollOptionUnvalidException(f"Error: PollOption with id={poll_option_id} does " +
            f"not exist or it is not related to Poll with id={self.__poll.id}")
        
        return self
    
    def perform_creation(self) -> VoteModel:
        
        if self.__vote_model is not None:
            return self.__vote_model

        self.__vote_model = VoteModel(poll_option=self.__voted_option)
        
        return self.__vote_model
