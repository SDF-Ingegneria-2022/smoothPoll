from typing import List
from django.core.exceptions import ObjectDoesNotExist
from polls.exceptions.poll_not_valid_creation_exception import PollNotValidCreationException
from polls.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
from polls.models import PollModel
from polls.models.poll_option_model import PollOptionModel


class PollService:
    """Class to handle all poll related operations"""
    
    @staticmethod
    def create(name: str, question: str, options: List[dict]) -> PollModel: 
        """Creates a new poll.
        Args:
            name: Name of the poll. It has to be at least 1 characters long.
            question: Question of the poll. It has to be at least 1 characters long.
            options: List of options for the poll. It has to have at least 1 option.
        Raises:
            PollNotValidCreationException: Is raised when the poll is not valid. When the input params not meet the requirements.
        Returns:
            PollModel: The created poll.
        """

        if len(name)<1 or len(question)<1 or len(options)<1:
            raise PollNotValidCreationException("Poll not valid for creation")
        
        new_poll: PollModel = PollModel(name=name, question=question)
        new_poll.save()
        
        for option in options:
            new_option: PollOptionModel = PollOptionModel(key=option["key"],value=option["value"], poll_fk_id=new_poll.id)
            new_option.save()
        
        return new_poll
    
    @staticmethod
    def get_poll_by_id(id:str) -> PollModel:
        """Get a poll by id.
        Args:
            id: Id of the poll.
        Raises:
            PollDoesNotExistException: raised when you retrieve a non-existent poll
        """

        try:
            poll: PollModel = PollModel.objects.get(id=id)
        except ObjectDoesNotExist:
            raise PollDoesNotExistException(f"Error: poll with id={id} does not exit")    
        
        return poll
