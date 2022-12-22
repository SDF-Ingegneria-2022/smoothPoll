from typing import List
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from apps.polls_management.classes.majority_poll_result_data import MajorityPollResultData
from apps.polls_management.classes.poll_result import PollResult
from apps.polls_management.exceptions.paginator_page_size_exception import PaginatorPageSizeException
from apps.polls_management.exceptions.poll_has_been_voted_exception import PollHasBeenVotedException
from apps.polls_management.exceptions.poll_not_valid_creation_exception import PollNotValidCreationException
from apps.polls_management.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
from apps.polls_management.exceptions.poll_not_yet_voted_exception import PollNotYetVodedException
from polls.models.poll_option_model import PollOptionModel
from apps.polls_management.services.majority_vote_service import MajorityVoteService
from apps.polls_management.services.vote_service import VoteService
from polls.models.poll_model import PollModel

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
        """Delete a poll by id. If a poll has already received at least one vote, it can't be deleted.
        
        Args:
            id: Id of the poll to delete. The poll can be a majotiry poll or a siglone option poll.
        
        Raises:
            PollDoesNotExistException: If the poll not exist.
            PollHasBeenVotedException: If the poll has already received at least one vote.
            
        Returns: 
            Tuple: A tuple with first element the total number of deletions made
            and the second element a dict with the relative details about deletion from the model perspective.
            
        Example:
            {3, {'polls.PollModel': 1, 'polls.PollOptionModel': 2}}
        """
        try:
            poll: PollModel = PollModel.objects.get(id=id)
            poll_type: PollModel.PollType = poll.PollType
        except ObjectDoesNotExist:
            raise PollDoesNotExistException(f"Poll with id={id} does not exit.")  
        
        if poll.poll_type == poll_type.MAJORITY_JUDJMENT:
            # Check if the majotiry judment poll has already received at least one vote
            try:
                MajorityVoteService.calculate_result(poll.id)
            except PollNotYetVodedException:
                pass
            else:
                raise PollHasBeenVotedException(f"Error: poll with id={id} can't be deleted: it has already been voted")
            
        else:
            # Check if the single option poll has already received at least one vote
            poll_results: PollResult = VoteService.calculate_result(poll.id)
            for option_result in poll_results.get_sorted_options():
                if option_result.n_votes != 0:
                    raise PollHasBeenVotedException(f"Error: poll with id={id} can't be deleted: it has already been voted")

        return poll.delete()
