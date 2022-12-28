import datetime
from typing import List, Tuple
import pytest
from assertpy import assert_that
from django.db import models
from django.core.paginator import Paginator
from apps.polls_management.classes.poll_form import PollForm
from apps.polls_management.exceptions.paginator_page_size_exception import PaginatorPageSizeException
from apps.polls_management.exceptions.poll_is_open_exception import PollIsOpenException
from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.models.poll_option_model import PollOptionModel
from apps.votes_results.services.majority_judgment_vote_service import MajorityJudjmentVoteService
from apps.polls_management.services.poll_create_service import PollCreateService
from apps.polls_management.services.poll_service import PollService
from apps.polls_management.exceptions.poll_not_valid_creation_exception import PollNotValidCreationException
from apps.polls_management.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
from apps.votes_results.services.single_option_vote_service import SingleOptionVoteService


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
        """Test delete poll, basic verification that it works (not open poll)"""
        poll = PollService.create(self.name, self.question, self.options)
        id = poll.id

        open_date = datetime.datetime(year=2025, month=12, day=31, hour=12, minute=12, tzinfo=datetime.timezone.utc)
        poll.open_datetime = open_date

        # to update the open_datetime value and is_open method of the model
        poll.save()

        assert_that(poll.open_datetime).is_not_none()

        assert_that(poll.is_open()).is_false()

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
    def test_delete_is_open(self):
        """Test delete poll that is already open"""
        poll = PollService.create(self.name, self.question, self.options)
        id = poll.id

        open_date = datetime.datetime(year=2022, month=12, day=12, hour=12, minute=12, tzinfo=datetime.timezone.utc)
        poll.open_datetime = open_date

        # to update the open_datetime value and is_open method of the model
        poll.save()

        assert_that(PollService.delete_poll)\
            .raises(PollIsOpenException)\
            .when_called_with(id=id)
    
    @pytest.mark.django_db
    def test_delete_check_istance_option(self):
        """Test delete poll and also its option"""
        poll = PollService.create(self.name, self.question, self.options)
        assert_that(poll).is_instance_of(PollModel)
        option_id = poll.options()[0].id
        id = poll.id

        open_date = datetime.datetime(year=2025, month=12, day=30, hour=12, minute=12, tzinfo=datetime.timezone.utc)
        poll.open_datetime = open_date

        # to update the open_datetime value and is_open method of the model
        poll.save()

        PollService.delete_poll(id)
        assert_that(SingleOptionVoteService.perform_vote) \
            .raises(PollDoesNotExistException) \
            .when_called_with(poll_id=id, poll_choice_id=option_id)
            
    # =================== END legacy creation mode ===================
    @pytest.mark.django_db      
    def test_delete_majority_poll(self, create_majority_poll):
        """Test delete poll with majority (not open)"""
        poll: PollModel = create_majority_poll

        open_date = datetime.datetime(year=2025, month=12, day=30, hour=12, minute=12, tzinfo=datetime.timezone.utc)
        poll.open_datetime = open_date

        # to update the open_datetime value and is_open method of the model
        poll.save()
        
        deletion: Tuple = PollService.delete_poll(poll.id)
        assert_that(deletion[0]).is_greater_than(0)
    
    @pytest.mark.django_db
    def test_delete_is_open_majority_poll(self, create_majority_poll):
        """Test if an open majority poll is called to be deleted"""

        majority_poll: PollModel = create_majority_poll
        majority_poll_options:  List[PollOptionModel] = majority_poll.options()
        majority_vote_choices: List = [{'poll_choice_id': option.id, 'rating': 1 } for option in majority_poll_options]
        
        open_date = datetime.datetime(year=2022, month=12, day=12, hour=12, minute=12, tzinfo=datetime.timezone.utc)
        majority_poll.open_datetime = open_date

        # to update the open_datetime value and is_open method of the model
        majority_poll.save()

        MajorityJudjmentVoteService.perform_vote(majority_vote_choices, majority_poll.id)
        
        assert_that(PollService.delete_poll) \
            .raises(PollIsOpenException) \
            .when_called_with(id=majority_poll.id)