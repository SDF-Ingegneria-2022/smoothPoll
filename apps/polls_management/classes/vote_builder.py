from polls.models.vote_model import VoteModel
from polls.models.poll_model import PollModel
from polls.models.poll_option_model import PollOptionModel
from apps.polls_management.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
from apps.polls_management.exceptions.poll_option_unvalid_exception import PollOptionUnvalidException

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

    If something goes wrong, proper exception will be thrown.

    At end of process object is NOT saved (call save() to do so)
    """

    def __init__(self) -> None:
        self.__voted_option = None
        self.__poll = None
        self.__vote_model = None
        

    def set_poll(self, poll_id: str) -> "PollVoteBuilder":
        """
        Set the poll you want to vote. It resets choosed option
        Args:
            poll_id: poll you want to vote
        Raises:
            PollDoesNotExistException: you passed a not existent poll
        """
        
        self.__voted_option = None
        
        try:
            self.__poll: PollModel = PollModel.objects.get(id=poll_id)
            # todo: add here "is open" filter
        except ObjectDoesNotExist:
            raise PollDoesNotExistException(f"Error: Poll with id={poll_id} does not exist")

        return self

    def set_voted_option(self, poll_option_id: str) -> "PollVoteBuilder":
        """
        Set the option you want to vote
        Args:
            poll_option_id: your choice you want to vote
        Raises:
            PollOptionUnvalidException: you passed an option that does not belong to poll
                or you passed a not existent option
        """
        
        try:
            self.__voted_option: PollOptionModel = PollOptionModel.objects \
                .filter(poll_fk=self.__poll.id) \
                .get(id=poll_option_id)

        except ObjectDoesNotExist:
            raise PollOptionUnvalidException(f"Error: PollOption with id={poll_option_id} does " +
            f"not exist or it is not related to Poll with id={self.__poll.id}")
        
        return self
    
    def perform_creation(self) -> VoteModel:
        """
        Create VoteModel instance using passed (and validated) poll and option. 
        instance is not yet saved. Call save() to store it in DB.
        Raises:
            PollDoesNotExistException: poll is unvalid
            PollOptionUnvalidException: poll option is unvalid
        """

        if self.__poll is None:
            raise PollDoesNotExistException()
        if self.__voted_option is None:
            raise PollOptionUnvalidException()
        
        if self.__vote_model is not None:
            return self.__vote_model

        self.__vote_model = VoteModel(poll_option=self.__voted_option)
        
        return self.__vote_model
