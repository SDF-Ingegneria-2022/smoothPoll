from typing import List
from polls.dtos.poll_dto import PollDto
from polls.dtos.poll_option_dto import PollOptionDto
from polls.models import PollModel
from polls.services.poll_option_service import PollOptionService


class PollService:
    """Class to handle all poll related operations"""
    
    @staticmethod
    def create(name: str, question: str, options: List[dict]) -> PollDto: 
        """Creates a new poll.
        Args:
            name: Name of the poll.
            question: Question of the poll.
            options: List of options for the poll.
        Returns:
            PollDto: The created poll
        """
        new_poll: PollModel = PollModel(name=name, question=question)
        new_poll.save()
        
        #TODO: Understand what is the "key" param porpouse.
        created_poll_options: List[PollOptionDto] = [PollOptionService.create(option["key"], option["value"], new_poll.id) for option in options]
        
        return PollDto(name=new_poll.name, question=new_poll.question, options=created_poll_options)
    
    def get_by_id(id:str) -> PollDto:
        """Get a poll by id.
        Args:
            id: Id of the poll.
        """
        poll: PollModel = PollModel.objects.get(id=id)
        poll_options: List[PollOptionDto] = PollOptionService.get_by_poll_id(poll.id)
        return PollDto(name=poll.name, question=poll.question, options=poll_options)
