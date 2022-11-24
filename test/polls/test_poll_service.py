from typing import List
import pytest
from assertpy import assert_that
from django.db import models
from polls.services.poll_service import PollService
from polls.exceptions.poll_not_valid_creation_exception import PollNotValidCreationException

class TestPollService:
    """Test suite that covers all methods in the PollService class"""

    name: str = "TestPollName"
    question: str = "What is your favorite poll option?"
    options: List[dict] = [
                                {"key": "key_1", "value": "Question 1"}, 
                                {"key": "key_2", "value": "Question 2"}
                            ]
    
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


                