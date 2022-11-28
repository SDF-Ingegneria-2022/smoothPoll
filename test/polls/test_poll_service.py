from typing import List
import pytest
from assertpy import assert_that
from django.db import models
from polls.models.poll_model import PollModel
from polls.models.poll_option_model import PollOptionModel
from polls.services.poll_service import PollService
from polls.exceptions.poll_not_valid_creation_exception import PollNotValidCreationException
from polls.exceptions.poll_does_not_exist_exception import PollDoesNotExistException


class TestPollService:
    """Test suite that covers all methods in the PollService class"""

    name: str = "TestPollName"
    question: str = "What is your favorite poll option?"
    # options: List[dict] = [
    #                             {"key": "key_1", "value": "Question 1"}, 
    #                             {"key": "key_2", "value": "Question 2"}
    #                         ]
    options: List[dict] = ["Question 1", "Question 2"]
    
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


