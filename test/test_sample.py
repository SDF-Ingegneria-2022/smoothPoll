
import pytest
from assertpy import assert_that
from polls.dtos.poll_dto import PollDto

from polls.services.poll_service import PollService
# content of test_class.py
class TestClass:
    def test_one(self):
        x = "this"  
        assert_that(x).contains("h")
    
    @pytest.mark.django_db
    def test_model(self):
        poll: PollDto = PollService.create("test", "test", [{"key": "test", "value": "test"}])
        assert poll.name == "test"