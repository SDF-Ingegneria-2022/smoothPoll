from polls.classes.poll_form import PollForm
from polls.models.poll_model import PollModel
from polls.models.poll_option_model import PollOptionModel
from polls.services.poll_create_service import PollCreateService
from polls.exceptions.poll_not_valid_creation_exception import *

from typing import Dict, List
import pytest
from assertpy import assert_that


class TestPollEdit:
    """Test suite that covers all methods in the PollService class"""

    name1: str = "Sondaggio cibo pt. 2"
    question1: str = "Ti piace la pizza?"
    options1: List[str] = ["Si", "No",]
    options2: List[str] = ["Si", "No", "Forse",]
    options3: List[str] = ["Si", "No", "Forse", "Potrebbe",]

    ## Fixtures
    @pytest.fixture
    def make_forms(self):
        """Create needed forms"""

        form1 = PollForm({"name": self.name1, "question": self.question1})

        return {"form1": form1,}

    @pytest.mark.django_db
    def test_edit_poll_runs(self, make_forms):
        """Simple test to check if edit after creation does not crash (it runs)"""
    
        PollCreateService.create_or_edit_poll(make_forms["form1"], self.options1)

        PollCreateService.create_or_edit_poll(make_forms["form1"], self.options2)
        

    @pytest.mark.django_db
    def test_edit_poll_ok(self, make_forms):
        """Check if object is edited, aside with all correct options"""
    
        poll = PollCreateService.create_or_edit_poll(make_forms["form1"], self.options1)

        # check data 
        assert_that(poll).is_instance_of(PollModel)
        assert_that(poll.name).is_equal_to(self.name1)
        assert_that(poll.question).is_equal_to(self.question1)

        # check it has been saved correctly
        assert_that(PollModel.objects.get(id=poll.id)).is_equal_to(poll)

        # check each options have been saved correctly
        assert_that(PollOptionModel.objects.filter(poll_fk=poll).count()).is_equal_to(self.options1.__len__())
        assert_that(poll.options().__len__()).is_equal_to(self.options1.__len__())

        # assert that all and only the input passed options are returned
        options_to_search = self.options1.copy()
        for o in poll.options():
            assert_that(o.value in options_to_search).is_true()
            options_to_search.remove(o.value)

        assert_that(options_to_search.__len__()).is_equal_to(0)

        # now check that edit works as expected
        poll2 = PollCreateService.create_or_edit_poll(make_forms["form1"], self.options2)

        # check it has been edited correctly
        assert_that(PollModel.objects.get(id=poll2.id)).is_equal_to(poll)
        assert_that(poll2.id).is_equal_to(poll.id)

        # check each options have been saved correctly
        assert_that(PollOptionModel.objects.filter(poll_fk=poll2).count()).is_equal_to(self.options2.__len__())
        assert_that(poll.options().__len__()).is_equal_to(self.options2.__len__())

        # assert that all and only the input passed options are returned
        options_to_search = self.options2.copy()
        for o in poll2.options():
            assert_that(o.value in options_to_search).is_true()
            options_to_search.remove(o.value)

        assert_that(options_to_search.__len__()).is_equal_to(0)





