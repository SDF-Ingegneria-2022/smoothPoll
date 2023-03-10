import datetime
from typing import List, Tuple
import pytest
from assertpy import assert_that
from django.db import models
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from apps.polls_management.classes.poll_form_utils.poll_form import PollForm
from apps.polls_management.exceptions.paginator_page_size_exception import PaginatorPageSizeException
from apps.polls_management.exceptions.poll_cannot_be_opened_exception import PollCannotBeOpenedException
from apps.polls_management.exceptions.poll_is_open_exception import PollIsOpenException
from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.models.poll_option_model import PollOptionModel
from apps.votes_results.services.majority_judgment_vote_service import MajorityJudjmentVoteService
from apps.polls_management.services.poll_create_service import PollCreateService
from apps.polls_management.services.poll_service import PollService
from apps.polls_management.exceptions.poll_not_valid_creation_exception import PollNotValidCreationException
from apps.polls_management.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
from apps.votes_results.services.single_option_vote_service import SingleOptionVoteService


class TestPollService():
    """Test suite that covers all methods in the PollService class"""

    name: str = "TestPollName"
    question: str = "What is your favorite poll option?"
    options: List[dict] = ["Question 1", "Question 2"]
    user: User = User(username="user1",password="bar1") 
    ## Fixtures
    @pytest.fixture
    def create_20_polls(self):
        """Creates 20 polls"""

        self.user.save()

        for poll_index in range(20):
            new_poll: PollModel = PollModel(name=f"Poll {poll_index}", question=f"Question {poll_index} ?",author=self.user)
            new_poll.save()
            for option_index in range(2):
                PollOptionModel(value=f"Option {option_index}", poll_fk_id=new_poll.id).save()
    
    @pytest.fixture
    def create_majority_poll(self) -> PollModel:
        """Creates a majority poll"""

        self.user.save()

        MAJORITY_JUDJMENT = "majority_judjment"
        majority_judjment_form: PollForm = PollForm({"name": "Form name", "question": "Form question", "poll_type": MAJORITY_JUDJMENT})
        majority_judjment_options: List[str] = ["Option 1", "Option 2", "Option 3"]
        return PollCreateService.create_or_edit_poll(majority_judjment_form, majority_judjment_options,user=self.user)
    
    ## Tests
    
    # =================== Legacy creation mode in the following tests ===================
    
    
    @pytest.mark.django_db
    def test_create(self):
        """Test the create method with a valid poll"""

        self.user.save()

        poll_created = PollService.create(self.name, self.question, self.options, self.user)

        assert_that(poll_created).is_instance_of(models.Model)
       
    @pytest.mark.django_db
    def test_create_with_wrong_name(self):
        """Test the create method with a poll with a wrong name"""
        name: str = ""

        self.user.save()

        assert_that(PollService.create).raises(PollNotValidCreationException).when_called_with(name, self.question, self.options, self.user)
    
    @pytest.mark.django_db
    def test_create_with_wrong_question(self):
        """Test the create method with a poll with a wrong question"""
        question: str = ""

        self.user.save()

        assert_that(PollService.create).raises(PollNotValidCreationException).when_called_with(self.name, question, self.options, self.user)

    @pytest.mark.django_db
    def test_create_with_wrong_options(self):
        """Test the create method with a poll with a wrong options"""
        options: List = []

        self.user.save()

        assert_that(PollService.create).raises(PollNotValidCreationException).when_called_with(self.name, self.question, options, self.user)

    @pytest.mark.django_db
    def test_view_poll(self):
        """Test get poll by id (basic verification it works)"""

        self.user.save()

        poll = PollService.create(self.name, self.question, self.options, self.user)
        retrieved_poll = PollService.get_poll_by_id(poll.id)

        assert_that(retrieved_poll).is_instance_of(PollModel)
        assert_that(retrieved_poll.name).is_equal_to(self.name)
        assert_that(retrieved_poll.question).is_equal_to(self.question)

    @pytest.mark.django_db
    def test_view_poll_options(self):
        """Test get poll by id (check options)"""

        self.user.save()

        poll = PollService.create(self.name, self.question, self.options, self.user)
        retrieved_poll = PollService.get_poll_by_id(poll.id)

        assert_that(retrieved_poll.options()).is_instance_of(list)
        assert_that(retrieved_poll.options()[0]).is_instance_of(PollOptionModel)
        assert_that(retrieved_poll.options()[0].id).is_equal_to(poll.options()[0].id)
    
    @pytest.mark.django_db
    def test_get_notexists_poll(self):
        """Test get poll that doesn't exists"""

        self.user.save()

        poll = PollService.create(self.name, self.question, self.options, self.user)
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
        
        self.user.save()

        poll = PollService.create(self.name, self.question, self.options, self.user)
        id = poll.id

        open_date = datetime.datetime(year=2050, month=12, day=31, hour=12, minute=12, tzinfo=datetime.timezone.utc)
        close_date = datetime.datetime(year=2100, month=12, day=31, hour=12, minute=12, tzinfo=datetime.timezone.utc)
        poll.open_datetime = open_date
        poll.close_datetime = close_date

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

        self.user.save()

        poll = PollService.create(self.name, self.question, self.options, self.user)
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

        self.user.save()

        poll = PollService.create(self.name, self.question, self.options, self.user)
        assert_that(poll).is_instance_of(PollModel)
        option_id = poll.options()[0].id
        id = poll.id

        open_date = datetime.datetime(year=2050, month=12, day=30, hour=12, minute=12, tzinfo=datetime.timezone.utc)
        close_date = datetime.datetime(year=2100, month=12, day=31, hour=12, minute=12, tzinfo=datetime.timezone.utc)
        poll.open_datetime = open_date
        poll.close_datetime = close_date

        # to update the open_datetime value and is_open method of the model
        poll.save()

        PollService.delete_poll(id)
        assert_that(SingleOptionVoteService.perform_vote) \
            .raises(PollDoesNotExistException) \
            .when_called_with(poll_id=id, poll_choice_id=option_id)
            

    @pytest.mark.django_db      
    def test_delete_majority_poll(self, create_majority_poll):
        """Test delete poll with majority (not open)"""
        poll: PollModel = create_majority_poll

        open_date = datetime.datetime(year=2050, month=12, day=30, hour=12, minute=12, tzinfo=datetime.timezone.utc)
        close_date = datetime.datetime(year=2100, month=12, day=31, hour=12, minute=12, tzinfo=datetime.timezone.utc)
        poll.open_datetime = open_date
        poll.close_datetime = close_date

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

    # ====== Open poll ======

    @pytest.mark.django_db
    def test_open_poll(self):
        """Test open poll, nonexistent poll"""

        self.user.save()

        poll = PollService.create(self.name, self.question, self.options, self.user)
        id = poll.id

        PollService.delete_poll(id)

        assert_that(PollService.open_poll) \
            .raises(PollDoesNotExistException) \
            .when_called_with(id=id)

    @pytest.mark.django_db
    def test_open_poll_already_open(self):
        """Test open poll, if poll is already open"""

        self.user.save()

        poll = PollService.create(self.name, self.question, self.options, self.user)
        id = poll.id

        open_date = datetime.datetime(year=2020, month=12, day=31, hour=12, minute=12, tzinfo=datetime.timezone.utc)
        poll.open_datetime = open_date

        # to update the open_datetime value and is_open method of the model
        poll.save()

        assert_that(poll.open_datetime).is_not_none()

        assert_that(poll.is_open()).is_true()

        assert_that(PollService.open_poll) \
            .raises(PollIsOpenException) \
            .when_called_with(id=id)

    @pytest.mark.django_db
    def test_open_poll_w_right_open_close_time(self):
        """Test open poll, open datetime and closetime not None"""

        self.user.save()

        poll = PollService.create(self.name, self.question, self.options, self.user)
        id = poll.id

        open_date = datetime.datetime(year=2050, month=12, day=30, hour=12, minute=12, tzinfo=datetime.timezone.utc)
        close_date = datetime.datetime(year=2100, month=12, day=31, hour=12, minute=12, tzinfo=datetime.timezone.utc)
        poll.open_datetime = open_date
        poll.close_datetime = close_date

        # to update the open_datetime value and is_open method of the model
        poll.save()

        assert_that(poll.open_datetime).is_not_none()
        assert_that(poll.close_datetime).is_not_none()

        assert_that(poll.is_open()).is_false()

        poll = PollService.open_poll(id)

        assert_that(poll.is_open()).is_true()

    @pytest.mark.django_db
    def test_open_poll_without_open_and_close_time(self):
        """Test open poll, no open and close time"""

        self.user.save()

        poll = PollService.create(self.name, self.question, self.options, self.user)
        id = poll.id

        assert_that(poll.open_datetime).is_none()

        assert_that(poll.is_open()).is_false()

        assert_that(PollService.open_poll) \
            .raises(PollCannotBeOpenedException) \
            .when_called_with(id=id)

    @pytest.mark.django_db
    def test_open_poll_without_close_time(self):
        """Test open poll, no close time"""

        self.user.save()

        poll = PollService.create(self.name, self.question, self.options, self.user)
        id = poll.id

        open_date = datetime.datetime(year=2100, month=12, day=31, hour=12, minute=12, tzinfo=datetime.timezone.utc)
        poll.open_datetime = open_date

        assert_that(poll.is_open()).is_false()

        assert_that(PollService.open_poll) \
            .raises(PollCannotBeOpenedException) \
            .when_called_with(id=id)

    @pytest.mark.django_db
    def test_open_poll_w_wrong_open_close_time(self):
        """Test open poll, open datetime and closetime not None but already passed"""

        self.user.save()

        poll = PollService.create(self.name, self.question, self.options, self.user)
        id = poll.id

        open_date = datetime.datetime(year=2020, month=12, day=30, hour=12, minute=12, tzinfo=datetime.timezone.utc)
        close_date = datetime.datetime(year=2022, month=12, day=31, hour=12, minute=12, tzinfo=datetime.timezone.utc)
        poll.open_datetime = open_date
        poll.close_datetime = close_date

        # to update the open_datetime value and is_open method of the model
        poll.save()

        assert_that(PollService.open_poll) \
            .raises(PollIsOpenException) \
            .when_called_with(id=id)

    # =================== END legacy creation mode ===================



    # ================= User polls section =================

    @pytest.mark.django_db
    def test_return_one_user_polls(self, create_20_polls):
        """Test that checks if the user poll service returns a list of user polls."""
        
        self.user.save()

        user_poll_list = PollService.user_polls(self.user)

        assert_that(user_poll_list).is_not_none()
        assert_that(user_poll_list).is_instance_of(List)
        assert_that(user_poll_list).is_length(20)

    @pytest.mark.django_db
    def test_return_different_users_polls(self, create_20_polls):
        """Test that checks if the user poll service returns the correct list of polls for different users."""
        
        self.user.save()

        user2: User = User(username="user2",password="bar1") 
        user2.save()

        user2pollsindex = int(30)

        while user2pollsindex > 0:
            polls2 = PollModel(name=self.name, question=self.question, author=user2)
            polls2.save()
            user2pollsindex -= 1

        user_poll_list1 = PollService.user_polls(self.user)
        user_poll_list2 = PollService.user_polls(user2)

        assert_that(user_poll_list1).is_not_none()
        assert_that(user_poll_list1).is_instance_of(List)
        assert_that(user_poll_list1).is_length(20)

        assert_that(user_poll_list2).is_not_none()
        assert_that(user_poll_list2).is_instance_of(List)
        assert_that(user_poll_list2).is_length(30)


    # ================= Active and votable polls section =================

    @pytest.mark.django_db
    def test_return_votable_poll_success(self):
        """Test that checks if there are votable polls and are successfully returned in a list."""

        self.user.save()

        pollsindex = int(3)

        while pollsindex > 0:
            polls = PollModel(name=self.name, question=self.question, author=self.user)
            open_date = datetime.datetime(year=2020, month=12, day=30, hour=12, minute=12, tzinfo=datetime.timezone.utc)
            close_date = datetime.datetime(year=2100, month=12, day=31, hour=12, minute=12, tzinfo=datetime.timezone.utc)
            polls.open_datetime = open_date
            polls.close_datetime = close_date
            polls.save()
            pollsindex -= 1

        votable_or_closed_polls_list = PollService.votable_or_closed_polls()
        
        assert_that(votable_or_closed_polls_list).is_not_none()
        assert_that(votable_or_closed_polls_list).is_instance_of(List)
        assert_that(votable_or_closed_polls_list).is_length(3)

    @pytest.mark.django_db
    def test_return_closed_poll_success(self):
        """Test that checks if there are closed polls and are successfully returned in a list."""

        self.user.save()

        pollsindex = int(3)

        while pollsindex > 0:
            polls = PollModel(name=self.name, question=self.question, author=self.user)
            open_date = datetime.datetime(year=2020, month=12, day=30, hour=12, minute=12, tzinfo=datetime.timezone.utc)
            close_date = datetime.datetime(year=2021, month=12, day=31, hour=12, minute=12, tzinfo=datetime.timezone.utc)
            polls.open_datetime = open_date
            polls.close_datetime = close_date
            polls.save()
            pollsindex -= 1

        votable_or_closed_polls_list = PollService.votable_or_closed_polls()

        assert_that(votable_or_closed_polls_list).is_not_none()
        assert_that(votable_or_closed_polls_list).is_instance_of(List)
        assert_that(votable_or_closed_polls_list).is_length(3)

    @pytest.mark.django_db
    def test_return_votable_and_closed_poll_success(self):
        """Test that checks if there are votable and closed polls and are successfully returned in a list."""

        self.user.save()

        pollsindex = int(30)

        while pollsindex > 0:
            polls = PollModel(name=self.name, question=self.question, author=self.user)
            open_date = datetime.datetime(year=2020, month=12, day=30, hour=12, minute=12, tzinfo=datetime.timezone.utc)
            close_date = datetime.datetime(year=2021, month=12, day=31, hour=12, minute=12, tzinfo=datetime.timezone.utc)
            polls.open_datetime = open_date
            polls.close_datetime = close_date
            polls.save()

            polls2 = PollModel(name=self.name, question=self.question, author=self.user)
            open_date2 = datetime.datetime(year=2020, month=12, day=30, hour=12, minute=12, tzinfo=datetime.timezone.utc)
            close_date2 = datetime.datetime(year=2100, month=12, day=31, hour=12, minute=12, tzinfo=datetime.timezone.utc)
            polls2.open_datetime = open_date2
            polls2.close_datetime = close_date2
            polls2.save()

            pollsindex -= 1

        votable_or_closed_polls_list = PollService.votable_or_closed_polls()

        assert_that(votable_or_closed_polls_list).is_not_none()
        assert_that(votable_or_closed_polls_list).is_instance_of(List)
        assert_that(votable_or_closed_polls_list).is_length(60)

    @pytest.mark.django_db
    def test_return_votable_and_closed_poll_with_other_polls_success(self):
        """Test that checks if there are votable and closed polls among other polls and are successfully returned in a list."""

        self.user.save()

        pollsindex = int(30)

        while pollsindex > 0:
            polls = PollModel(name=self.name, question=self.question, author=self.user)
            open_date = datetime.datetime(year=2020, month=12, day=30, hour=12, minute=12, tzinfo=datetime.timezone.utc)
            close_date = datetime.datetime(year=2021, month=12, day=31, hour=12, minute=12, tzinfo=datetime.timezone.utc)
            polls.open_datetime = open_date
            polls.close_datetime = close_date
            polls.save()

            polls2 = PollModel(name=self.name, question=self.question, author=self.user)
            open_date2 = datetime.datetime(year=2020, month=12, day=30, hour=12, minute=12, tzinfo=datetime.timezone.utc)
            close_date2 = datetime.datetime(year=2100, month=12, day=31, hour=12, minute=12, tzinfo=datetime.timezone.utc)
            polls2.open_datetime = open_date2
            polls2.close_datetime = close_date2
            polls2.save()

            polls3 = PollModel(name=self.name, question=self.question, author=self.user)
            polls3.save()

            pollsindex -= 1

        votable_or_closed_polls_list = PollService.votable_or_closed_polls()

        assert_that(votable_or_closed_polls_list).is_not_none()
        assert_that(votable_or_closed_polls_list).is_instance_of(List)
        assert_that(votable_or_closed_polls_list).is_length(60)

    @pytest.mark.django_db
    def test_return_votable_and_closed_poll_correct_order_success1(self):
        """Test that checks if the order of the list is correct."""

        self.user.save()

        poll1 = PollModel(name=self.name, question=self.question, author=self.user)
        open_date1 = datetime.datetime(year=2020, month=12, day=30, hour=12, minute=12, tzinfo=datetime.timezone.utc)
        close_date1 = datetime.datetime(year=2100, month=1, day=30, hour=12, minute=12, tzinfo=datetime.timezone.utc)
        poll1.open_datetime = open_date1
        poll1.close_datetime = close_date1
        poll1.save()

        poll2 = PollModel(name=self.name, question=self.question, author=self.user)
        open_date2 = datetime.datetime(year=2020, month=12, day=30, hour=12, minute=12, tzinfo=datetime.timezone.utc)
        close_date2 = datetime.datetime(year=2100, month=3, day=30, hour=12, minute=12, tzinfo=datetime.timezone.utc)
        poll2.open_datetime = open_date2
        poll2.close_datetime = close_date2
        poll2.save()

        poll3 = PollModel(name=self.name, question=self.question, author=self.user)
        open_date3 = datetime.datetime(year=2020, month=12, day=30, hour=12, minute=12, tzinfo=datetime.timezone.utc)
        close_date3 = datetime.datetime(year=2100, month=6, day=30, hour=12, minute=12, tzinfo=datetime.timezone.utc)
        poll3.open_datetime = open_date3
        poll3.close_datetime = close_date3
        poll3.save()

        poll4 = PollModel(name=self.name, question=self.question, author=self.user)
        open_date4 = datetime.datetime(year=2020, month=12, day=30, hour=12, minute=12, tzinfo=datetime.timezone.utc)
        close_date4 = datetime.datetime(year=2100, month=12, day=31, hour=12, minute=12, tzinfo=datetime.timezone.utc)
        poll4.open_datetime = open_date4
        poll4.close_datetime = close_date4
        poll4.save()

        votable_or_closed_polls_list = PollService.votable_or_closed_polls()

        assert_that(votable_or_closed_polls_list).is_not_none()
        assert_that(votable_or_closed_polls_list).is_instance_of(List)
        assert_that(votable_or_closed_polls_list).is_length(4)

        assert_that(votable_or_closed_polls_list[0].id).is_equal_to(poll1.id)
        assert_that(votable_or_closed_polls_list[1].id).is_equal_to(poll2.id)
        assert_that(votable_or_closed_polls_list[2].id).is_equal_to(poll3.id)
        assert_that(votable_or_closed_polls_list[3].id).is_equal_to(poll4.id)

    @pytest.mark.django_db
    def test_return_votable_and_closed_poll_correct_order_success2(self):
        """Test that checks if the order of the list is correct (reversed order)."""

        self.user.save()

        poll1 = PollModel(name=self.name, question=self.question, author=self.user)
        open_date1 = datetime.datetime(year=2020, month=12, day=30, hour=12, minute=12, tzinfo=datetime.timezone.utc)
        close_date1 = datetime.datetime(year=2100, month=12, day=31, hour=12, minute=12, tzinfo=datetime.timezone.utc)
        poll1.open_datetime = open_date1
        poll1.close_datetime = close_date1
        poll1.save()

        poll2 = PollModel(name=self.name, question=self.question, author=self.user)
        open_date2 = datetime.datetime(year=2020, month=12, day=30, hour=12, minute=12, tzinfo=datetime.timezone.utc)
        close_date2 = datetime.datetime(year=2100, month=6, day=30, hour=12, minute=12, tzinfo=datetime.timezone.utc)
        poll2.open_datetime = open_date2
        poll2.close_datetime = close_date2
        poll2.save()

        poll3 = PollModel(name=self.name, question=self.question, author=self.user)
        open_date3 = datetime.datetime(year=2020, month=12, day=30, hour=12, minute=12, tzinfo=datetime.timezone.utc)
        close_date3 = datetime.datetime(year=2100, month=3, day=30, hour=12, minute=12, tzinfo=datetime.timezone.utc)
        poll3.open_datetime = open_date3
        poll3.close_datetime = close_date3
        poll3.save()

        poll4 = PollModel(name=self.name, question=self.question, author=self.user)
        open_date4 = datetime.datetime(year=2020, month=12, day=30, hour=12, minute=12, tzinfo=datetime.timezone.utc)
        close_date4 = datetime.datetime(year=2100, month=1, day=30, hour=12, minute=12, tzinfo=datetime.timezone.utc)
        poll4.open_datetime = open_date4
        poll4.close_datetime = close_date4
        poll4.save()

        votable_or_closed_polls_list = PollService.votable_or_closed_polls()

        assert_that(votable_or_closed_polls_list).is_not_none()
        assert_that(votable_or_closed_polls_list).is_instance_of(List)
        assert_that(votable_or_closed_polls_list).is_length(4)

        assert_that(votable_or_closed_polls_list[0].id).is_equal_to(poll4.id)
        assert_that(votable_or_closed_polls_list[1].id).is_equal_to(poll3.id)
        assert_that(votable_or_closed_polls_list[2].id).is_equal_to(poll2.id)
        assert_that(votable_or_closed_polls_list[3].id).is_equal_to(poll1.id)

    @pytest.mark.django_db
    def test_return_votable_and_closed_poll_correct_order_success3(self):
        """Test that checks if the order of the list is correct (reversed order and closed polls too)."""

        self.user.save()

        # open polls

        poll1 = PollModel(name=self.name, question=self.question, author=self.user)
        open_date1 = datetime.datetime(year=2020, month=12, day=30, hour=12, minute=12, tzinfo=datetime.timezone.utc)
        close_date1 = datetime.datetime(year=2100, month=12, day=31, hour=12, minute=12, tzinfo=datetime.timezone.utc)
        poll1.open_datetime = open_date1
        poll1.close_datetime = close_date1
        poll1.save()

        poll2 = PollModel(name=self.name, question=self.question, author=self.user)
        open_date2 = datetime.datetime(year=2020, month=12, day=30, hour=12, minute=12, tzinfo=datetime.timezone.utc)
        close_date2 = datetime.datetime(year=2100, month=6, day=30, hour=12, minute=12, tzinfo=datetime.timezone.utc)
        poll2.open_datetime = open_date2
        poll2.close_datetime = close_date2
        poll2.save()

        poll3 = PollModel(name=self.name, question=self.question, author=self.user)
        open_date3 = datetime.datetime(year=2020, month=12, day=30, hour=12, minute=12, tzinfo=datetime.timezone.utc)
        close_date3 = datetime.datetime(year=2100, month=3, day=30, hour=12, minute=12, tzinfo=datetime.timezone.utc)
        poll3.open_datetime = open_date3
        poll3.close_datetime = close_date3
        poll3.save()

        poll4 = PollModel(name=self.name, question=self.question, author=self.user)
        open_date4 = datetime.datetime(year=2020, month=12, day=30, hour=12, minute=12, tzinfo=datetime.timezone.utc)
        close_date4 = datetime.datetime(year=2100, month=1, day=30, hour=12, minute=12, tzinfo=datetime.timezone.utc)
        poll4.open_datetime = open_date4
        poll4.close_datetime = close_date4
        poll4.save()

        # closed polls

        poll5 = PollModel(name=self.name, question=self.question, author=self.user)
        open_date5 = datetime.datetime(year=2020, month=12, day=30, hour=12, minute=12, tzinfo=datetime.timezone.utc)
        close_date5 = datetime.datetime(year=2021, month=10, day=30, hour=12, minute=12, tzinfo=datetime.timezone.utc)
        poll5.open_datetime = open_date5
        poll5.close_datetime = close_date5
        poll5.save()

        poll6 = PollModel(name=self.name, question=self.question, author=self.user)
        open_date6 = datetime.datetime(year=2020, month=12, day=30, hour=12, minute=12, tzinfo=datetime.timezone.utc)
        close_date6 = datetime.datetime(year=2021, month=4, day=30, hour=12, minute=12, tzinfo=datetime.timezone.utc)
        poll6.open_datetime = open_date6
        poll6.close_datetime = close_date6
        poll6.save()

        poll7 = PollModel(name=self.name, question=self.question, author=self.user)
        open_date7 = datetime.datetime(year=2020, month=12, day=30, hour=12, minute=12, tzinfo=datetime.timezone.utc)
        close_date7 = datetime.datetime(year=2021, month=1, day=30, hour=12, minute=12, tzinfo=datetime.timezone.utc)
        poll7.open_datetime = open_date7
        poll7.close_datetime = close_date7
        poll7.save()

        votable_or_closed_polls_list = PollService.votable_or_closed_polls()

        assert_that(votable_or_closed_polls_list).is_not_none()
        assert_that(votable_or_closed_polls_list).is_instance_of(List)
        assert_that(votable_or_closed_polls_list).is_length(7)

        assert_that(votable_or_closed_polls_list[0].id).is_equal_to(poll4.id)
        assert_that(votable_or_closed_polls_list[1].id).is_equal_to(poll3.id)
        assert_that(votable_or_closed_polls_list[2].id).is_equal_to(poll2.id)
        assert_that(votable_or_closed_polls_list[3].id).is_equal_to(poll1.id)
        assert_that(votable_or_closed_polls_list[4].id).is_equal_to(poll5.id)
        assert_that(votable_or_closed_polls_list[5].id).is_equal_to(poll6.id)
        assert_that(votable_or_closed_polls_list[6].id).is_equal_to(poll7.id)