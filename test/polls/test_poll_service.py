from typing import List, Tuple
import pytest
from assertpy import assert_that
from django.db import models
from django.core.paginator import Paginator
from apps.polls_management.classes.poll_form import PollForm
from apps.polls_management.classes.poll_result import PollResult, PollResultVoice
from apps.polls_management.exceptions.paginator_page_size_exception import PaginatorPageSizeException
from apps.polls_management.exceptions.poll_has_been_voted_exception import PollHasBeenVotedException
from apps.polls_management.exceptions.poll_option_unvalid_exception import PollOptionUnvalidException
from polls.models.majority_vote_model import MajorityVoteModel
from polls.models.poll_model import PollModel
from polls.models.poll_option_model import PollOptionModel
from apps.polls_management.services.majority_vote_service import MajorityVoteService
from apps.polls_management.services.poll_create_service import PollCreateService
from apps.polls_management.services.poll_service import PollService
from apps.polls_management.exceptions.poll_not_valid_creation_exception import PollNotValidCreationException
from apps.polls_management.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
from apps.polls_management.services.vote_service import VoteService


class TestPollService:
    """Test suite that covers all methods in the PollService class"""

    name: str = "TestPollName"
    question: str = "What is your favorite poll option?"
    options: List[dict] = ["Question 1", "Question 2"]

    ## Fixtures
    @pytest.fixture
    def create_20_polls(self):
        """Creates 20 polls"""
        for poll_index in range(20):
            new_poll: PollModel = PollModel(name=f"Poll {poll_index}", question=f"Question {poll_index} ?")
            new_poll.save()
            for option_index in range(2):
                PollOptionModel(value=f"Option {option_index}", poll_fk_id=new_poll.id).save()
    
    @pytest.fixture
    def create_majority_poll(self) -> PollModel:
        """Creates a majotiry poll"""
        MAJORITY_JUDJMENT = "majority_judjment"
        majority_judjment_form: PollForm = PollForm({"name": "Form name", "question": "Form question", "poll_type": MAJORITY_JUDJMENT})
        majority_judjment_options: List[str] = ["Option 1", "Option 2", "Option 3"]
        return PollCreateService.create_or_edit_poll(majority_judjment_form, majority_judjment_options)
        
         
    
    ## Tests
    
    # =================== Legacy creation mode in the following tests ===================
    
    
    @pytest.mark.django_db
    def test_create(self):
        """Test the create method with a valid poll"""
        
        poll_created = PollService.create(self.name, self.question, self.options)

        assert_that(poll_created).is_instance_of(models.Model)
       
    @pytest.mark.django_db
    def test_create_with_wrong_name(self):
        """Test the create method with a poll with a wrong name"""
        name: str = ""

        assert_that(PollService.create).raises(PollNotValidCreationException).when_called_with(name, self.question, self.options)
    
    @pytest.mark.django_db
    def test_create_with_wrong_question(self):
        """Test the create method with a poll with a wrong question"""
        question: str = ""

        assert_that(PollService.create).raises(PollNotValidCreationException).when_called_with(self.name, question, self.options)

    @pytest.mark.django_db
    def test_create_with_wrong_options(self):
        """Test the create method with a poll with a wrong options"""
        options: List = []

        assert_that(PollService.create).raises(PollNotValidCreationException).when_called_with(self.name, self.question, options)

    @pytest.mark.django_db
    def test_view_poll(self):
        """Test get poll by id (basic verification it works)"""

        poll = PollService.create(self.name, self.question, self.options)
        retrieved_poll = PollService.get_poll_by_id(poll.id)

        assert_that(retrieved_poll).is_instance_of(PollModel)
        assert_that(retrieved_poll.name).is_equal_to(self.name)
        assert_that(retrieved_poll.question).is_equal_to(self.question)

    @pytest.mark.django_db
    def test_view_poll_options(self):
        """Test get poll by id (check options)"""

        poll = PollService.create(self.name, self.question, self.options)
        retrieved_poll = PollService.get_poll_by_id(poll.id)

        assert_that(retrieved_poll.options()).is_instance_of(list)
        assert_that(retrieved_poll.options()[0]).is_instance_of(PollOptionModel)
        assert_that(retrieved_poll.options()[0].id).is_equal_to(poll.options()[0].id)
    
    @pytest.mark.django_db
    def test_get_notexists_poll(self):
        """Test get poll that doesn't exists"""

        poll = PollService.create(self.name, self.question, self.options)
        id = poll.id
        poll.delete()

        assert_that(PollService.get_poll_by_id) \
            .raises(PollDoesNotExistException) \
            .when_called_with(id=id)

    
    @pytest.mark.django_db
    def test_get_paginated_polls_check_instance(self, create_20_polls):
        """Test get paginated polls with 20 polls and 5 polls per page and check the instance of the returned object"""
        polls_paginated: Paginator = PollService.get_paginated_polls(5)

        assert_that(polls_paginated).is_instance_of(Paginator)
    
    @pytest.mark.django_db
    def test_get_paginated_not_valid_items_per_page(self, create_20_polls):
        """Test get paginated polls with 20 polls and 5 polls per page and check the instance of the returned object"""
        items_per_page: int = 0

        assert_that(PollService.get_paginated_polls).raises(PaginatorPageSizeException).when_called_with(items_per_page)
    
    # ====== Delete poll ======
    @pytest.mark.django_db
    def test_delete_poll(self):
        """Test delete poll, basic verification that it works"""
        poll = PollService.create(self.name, self.question, self.options)
        id = poll.id
        assert_that(poll).is_instance_of(PollModel)
        PollService.delete_poll(poll.id)
        assert_that(PollService.delete_poll)\
            .raises(PollDoesNotExistException)\
            .when_called_with(id=id)


    @pytest.mark.django_db
    def test_delete_notexists_poll(self):
        """Test delete poll that doesn't exists"""
        #hardcode, need to verify
        id = 0
        assert_that(PollService.delete_poll) \
            .raises(PollDoesNotExistException) \
            .when_called_with(id=id)
    
    @pytest.mark.django_db
    def test_delete_already_voted_poll(self):
        """Test delete poll that has been already voted"""
        poll = PollService.create(self.name, self.question, self.options)
        VoteService.perform_vote(poll_id=poll.id, poll_choice_id=poll.options()[0].id)
        id = poll.id
        assert_that(PollService.delete_poll) \
            .raises(PollHasBeenVotedException) \
            .when_called_with(id=id)
    
    @pytest.mark.django_db
    def test_delete_check_istance_option(self):
        """Test delete poll and also its option"""
        poll = PollService.create(self.name, self.question, self.options)
        assert_that(poll).is_instance_of(PollModel)
        option_id = poll.options()[0].id
        id = poll.id
        PollService.delete_poll(id)
        assert_that(VoteService.perform_vote) \
            .raises(PollDoesNotExistException) \
            .when_called_with(poll_id=id, poll_choice_id=option_id)
            
    # =================== END legacy creation mode ===================
    @pytest.mark.django_db      
    def test_delete_majority_poll(self, create_majority_poll):
        """Test delete poll with majority"""
        poll: PollModel = create_majority_poll
        
        deletion: Tuple = PollService.delete_poll(poll.id)
        assert_that(deletion[0]).is_greater_than(0)
    
    @pytest.mark.django_db
    def test_delete_already_voted_majority_poll(self, create_majority_poll):
        majority_poll: PollModel = create_majority_poll
        majority_poll_options:  List[PollOptionModel] = majority_poll.options()
        majority_vote_choices: List = [{'poll_choice_id': option.id, 'rating': 1 } for option in majority_poll_options]
        
        MajorityVoteService.perform_vote(majority_vote_choices, majority_poll.id)
        
        assert_that(PollService.delete_poll) \
            .raises(PollHasBeenVotedException) \
            .when_called_with(id=majority_poll.id)