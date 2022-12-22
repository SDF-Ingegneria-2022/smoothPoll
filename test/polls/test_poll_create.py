from apps.polls_management.classes.poll_form import PollForm
from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.models.poll_option_model import PollOptionModel
from apps.polls_management.services.poll_create_service import PollCreateService
from apps.polls_management.exceptions.poll_not_valid_creation_exception import *

from typing import Dict, List
import pytest
from assertpy import assert_that


class TestPollCreate:
    """Test suite that covers all methods in the PollService class"""

    
    name1: str = "Sondaggio cibo pt. 2"
    question1: str = "Ti piace la pizza?"
    options1: List[str] = ["Si", "No",]
    
    name2: str = "Sondaggio cibo pt. 2"
    question2: str = "Qual è il tuo cibo preferito?"
    options2: List[str] = ["Pizza", "Pasta", "Carne", "Pesce", "Altro", ]
    type2: str = PollModel.PollType.MAJORITY_JUDJMENT

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
        form2 = PollForm({
            "name": self.name2, 
            "question": self.question2, 
            "poll_type": self.type2
            })

        return {"form1": form1, "form2": form2,}

    @pytest.mark.django_db
    def test_create_poll_runs(self, make_forms):
        """Simple test to check if creation does not crash (it runs)"""
    
        PollCreateService.create_or_edit_poll(make_forms["form1"], self.options1)
        

    @pytest.mark.django_db
    def test_create_poll_ok1(self, make_forms):
        """Check if object is created, aside with all options"""
    
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

    @pytest.mark.django_db
    def test_create_missing_name(self, make_forms):
        """Check what happend if I don't insert name"""

        form = make_forms["form1"]
        form.data["name"] = " "

        assert_that(PollCreateService.create_or_edit_poll) \
            .raises(PollMainDataNotValidException) \
            .when_called_with(poll_form=form, options=self.options1)

    @pytest.mark.django_db
    def test_create_missing_question(self, make_forms):
        """Check what happend if I don't insert question"""

        form = make_forms["form1"]
        form.data["question"] = None

        assert_that(PollCreateService.create_or_edit_poll) \
            .raises(PollMainDataNotValidException) \
            .when_called_with(poll_form=form, options=self.options1)

    @pytest.mark.django_db
    def test_create_few_options_1(self, make_forms):
        """Check what happend if I don't insert enough options"""

        assert_that(PollCreateService.create_or_edit_poll) \
            .raises(TooFewOptionsException) \
            .when_called_with(poll_form=make_forms["form1"], options=self.options_few1)

    @pytest.mark.django_db
    def test_create_few_options_2(self, make_forms):
        """Check what happend if I don't insert enough options
        (ensuring empty space is not consiederd a valid option)"""

        assert_that(PollCreateService.create_or_edit_poll) \
            .raises(TooFewOptionsException) \
            .when_called_with(poll_form=make_forms["form1"], options=self.options_few2)

    @pytest.mark.django_db
    def test_create_too_many_options(self, make_forms):
        """Check what happend if I insert too many options"""

        assert_that(PollCreateService.create_or_edit_poll) \
            .raises(TooManyOptionsException) \
            .when_called_with(poll_form=make_forms["form1"], options=self.options_many)

    ## ------------------------------------
    ## Test Majoriry Judjment creation

    @pytest.mark.django_db
    def test_create_missing_type(self, make_forms):
        """Check what happend if I don't set type
        (I expect a classic single option poll)"""

        poll = PollCreateService.create_or_edit_poll(
            make_forms["form1"], 
            self.options1)

        assert_that(poll.poll_type).is_equal_to(PollModel.PollType.SINGLE_OPTION)


    @pytest.mark.django_db
    def test_create_majority_judjment(self, make_forms):
        """Create a majority judment poll and 
        ensure type is right"""

        poll = PollCreateService.create_or_edit_poll(
            make_forms["form2"], 
            self.options2)

        # ensure type is MajorityJudment
        assert_that(poll.poll_type).is_equal_to(self.type2)

    @pytest.mark.django_db
    def test_create_majority_judjment_few_options(self, make_forms):
        """A majority judment poll should have at least 3 options. 
        We try passing 2 and we expect an exception"""

        assert_that(PollCreateService.create_or_edit_poll) \
            .raises(TooFewOptionsException) \
            .when_called_with(
                poll_form=make_forms["form2"], 
                # pass just 2 options instead of 3
                options=self.options1)

    @pytest.mark.django_db
    def test_form_get_min_options(self, make_forms):
        """ensure form objects return correct number
        of min options foreach poll type"""

        assert_that(make_forms["form1"].get_min_options()).is_equal_to(2)
        assert_that(make_forms["form2"].get_min_options()).is_equal_to(3)

    @pytest.mark.django_db
    def test_form_get_type_verbose_name(self, make_forms):
        """ensure form objects return correct 
        verbose name forach poll type"""

        assert_that(make_forms["form1"].get_type_verbose_name()).is_equal_to("Opzione Singola")
        assert_that(make_forms["form2"].get_type_verbose_name()).is_equal_to("Giudizio Maggioritario")

    




