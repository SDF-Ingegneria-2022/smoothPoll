from polls.classes.poll_form import PollForm
from polls.models.poll_model import PollModel
from polls.models.poll_option_model import PollOptionModel
from polls.services.poll_create_service import PollCreateService
from polls.exceptions.poll_not_valid_creation_exception import *

from typing import Dict, List
import pytest
from assertpy import assert_that


class TestPollCreationService:
    """Test suite that covers all methods in the PollService class"""

    name1: str = "Sondaggio cibo"
    question1: str = "Qual è il tuo cibo preferito?"
    options1: List[str] = ["Pizza", "Pasta", "Carne", "Pesce", "Altro", ]

    name2: str = "Sondaggio cibo pt. 2"
    question2: str = "Ti piace il pesce crudo?"
    options2: List[str] = ["Si", "No",]

    options_few1: List[str] = ["Si :)", ]
    options_few2: List[str] = ["Si :)", " "]
    options_many: List[str] = [str(i) for i in range(1,12)] 
    """numbers from 1 to 11 as str 
    (too many for current options constrains)"""

    ## Fixtures
    @pytest.fixture
    def make_forms(self):
        """Create needed forms"""
        form1 = PollForm({"name": self.name1, "question": self.question1})
        form2 = PollForm({"name": self.name2, "question": self.question2})

        return {"form1": form1, "form2": form2,}

    @pytest.mark.django_db
    def test_create_poll_runs(self, make_forms):
        """Simple test to check if creation does not crash (it runs)"""
    
        PollCreateService.create_new_poll(make_forms["form1"], self.options1)
        

    @pytest.mark.django_db
    def test_create_poll_ok1(self, make_forms):
        """Check if object is created, aside with all options"""
    
        poll = PollCreateService.create_new_poll(make_forms["form1"], self.options1)

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

    @pytest.mark.django_db
    def test_create_missing_name(self, make_forms):
        """Check what happend if I don't insert name"""

        form = make_forms["form1"]
        form.data["name"] = " "

        assert_that(PollCreateService.create_new_poll) \
            .raises(NameOrQuestionNotValidException) \
            .when_called_with(poll_form=form, options=self.options1)

    @pytest.mark.django_db
    def test_create_missing_question(self, make_forms):
        """Check what happend if I don't insert question"""

        form = make_forms["form1"]
        form.data["question"] = None

        assert_that(PollCreateService.create_new_poll) \
            .raises(NameOrQuestionNotValidException) \
            .when_called_with(poll_form=form, options=self.options1)

    @pytest.mark.django_db
    def test_create_few_options_1(self, make_forms):
        """Check what happend if I don't insert enough options"""

        assert_that(PollCreateService.create_new_poll) \
            .raises(TooFewOptionsException) \
            .when_called_with(poll_form=make_forms["form1"], options=self.options_few1)

    @pytest.mark.django_db
    def test_create_few_options_2(self, make_forms):
        """Check what happend if I don't insert enough options
        (ensuring empty space is not consiederd a valid option)"""

        assert_that(PollCreateService.create_new_poll) \
            .raises(TooFewOptionsException) \
            .when_called_with(poll_form=make_forms["form1"], options=self.options_few2)

    


