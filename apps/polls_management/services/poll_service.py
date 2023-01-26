from typing import List
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from apps.polls_management.classes.majority_poll_result_data import MajorityPollResultData
from apps.polls_management.classes.poll_result import PollResult
from apps.polls_management.exceptions.paginator_page_size_exception import PaginatorPageSizeException
from apps.polls_management.exceptions.poll_cannot_be_opened_exception import PollCannotBeOpenedException
from apps.polls_management.exceptions.poll_has_been_voted_exception import PollHasBeenVotedException
from apps.polls_management.exceptions.poll_is_open_exception import PollIsOpenException
from apps.polls_management.exceptions.poll_not_valid_creation_exception import PollNotValidCreationException
from apps.polls_management.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
from apps.polls_management.exceptions.poll_not_yet_voted_exception import PollNotYetVodedException
from apps.polls_management.models.poll_option_model import PollOptionModel
from apps.votes_results.services.majority_judgment_vote_service import MajorityJudjmentVoteService
from apps.votes_results.services.single_option_vote_service import SingleOptionVoteService
from apps.polls_management.models.poll_model import PollModel
from django.utils import timezone

class PollService:
    """Class to handle all poll related operations"""
    
    #TODO: check if this method is legacy
    @staticmethod
    def create(name: str, question: str, options: List[str]) -> PollModel: 
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
            # new_option: PollOptionModel = PollOptionModel(key=option["key"],value=option["value"], poll_fk_id=new_poll.id)
            new_option: PollOptionModel = PollOptionModel(value=option, poll_fk_id=new_poll.id)
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
    
    @staticmethod
    def get_paginated_polls(page_size: int = 10) -> Paginator:
        """Get a paginated list of polls. The page size is 10 by default.

        Args:
            page_size: Number of polls per page. It has to be al least 1. By default is 10.
        
        Raises:
            PaginatorPageSizeException: raised when the page size is not valid. When the page size is less than 1.
        Returns:
            Paginator: A paginator object with the polls.
        """
        if page_size < 1:
            raise PaginatorPageSizeException(f"Page size: {page_size} is not valid: It must be at least 1")

        # polls: List[PollModel] = PollModel.objects.get_queryset() \
        #     .filter(poll_type='single_option').order_by('id')

        polls: List[PollModel] = PollModel.objects.all().order_by('id')
        
        paginator: Paginator = Paginator(polls, page_size)
        
        return paginator
    
    @staticmethod
    def delete_poll(id:str):
        """Delete a poll by id. If a poll has already been opened, it can't be deleted.
        
        Args:
            id: Id of the poll to delete. The poll can be a majority poll or a single option poll.
        
        Raises:
            PollDoesNotExistException: If the poll not exist.
            PollIsOpenException: If the poll is open.
            
        Returns: 
            Tuple: A tuple with first element the total number of deletions made
            and the second element a dict with the relative details about deletion from the model perspective.
            
        Example:
            {3, {'polls.PollModel': 1, 'polls.PollOptionModel': 2}}
        """
        try:
            poll: PollModel = PollModel.objects.get(id=id)
        except ObjectDoesNotExist:
            raise PollDoesNotExistException(f"Poll with id={id} does not exit.")  
        
        if poll.is_open() or poll.is_closed():
            raise PollIsOpenException(f"Poll with id={id} is open.")

        return poll.delete()

    @staticmethod
    def open_poll(id:str):
        """Open a poll by id. If a poll has already been opened, it can't be opened.
        
        Args:
            id: Id of the poll to open. The poll can be a majority poll or a single option poll.
        
        Raises:
            PollDoesNotExistException: If the poll not exist.
            PollIsOpenException: If the poll is already open.
            PollCannotBeOpenedException: If the poll open and close time is not valid.
            
        Returns: 
            PollModel: the opened poll.
        """
        try:
            poll: PollModel = PollModel.objects.get(id=id)
        except ObjectDoesNotExist:
            raise PollDoesNotExistException(f"Poll with id={id} does not exit.")  
        
        if poll.is_open():
            raise PollIsOpenException(f"Poll with id={id} is already open.")

        if poll.open_datetime and poll.close_datetime and timezone.now() < poll.close_datetime:
            poll.open_datetime = timezone.now()
            poll.save()

            return poll
            
        else:
            raise PollCannotBeOpenedException(f"Poll with id={id} cannot be opened.")
    
