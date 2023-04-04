from apps.polls_management.classes.poll_form_utils.poll_form import PollForm
from apps.polls_management.exceptions.poll_is_open_exception import PollIsOpenException
from apps.polls_management.models.poll_model import SHORT_ID, PollModel
from apps.polls_management.models.poll_option_model import PollOptionModel
from apps.polls_management.services.poll_create_service import PollCreateService
from apps.polls_management.exceptions.poll_not_valid_creation_exception import *

from typing import Dict, List
import pytest
from assertpy import assert_that
# from django.db import models
import datetime


class TestPollCreate:
    """Test suite that covers all methods in the PollService class"""

    
    name1: str = "Scelta cibo pt. 2"
    question1: str = "Ti piace la pizza?"
    options1: List[str] = ["Si", "No",]
    
    name2: str = "Scelta cibo pt. 2"
    question2: str = "Qual è il tuo cibo preferito?"
    options2: List[str] = ["Pizza", "Pasta", "Carne", "Pesce", "Altro", ]
    type2: str = PollModel.PollType.MAJORITY_JUDJMENT

    options_few1: List[str] = ["Si :)", ]
    options_few2: List[str] = ["Si :)", " "]
    options_many: List[str] = [str(i) for i in range(1,12)] 
    """numbers from 1 to 11 as str 
    (too many for current options constrains)"""

    too_short_id = "12345"
    not_valid_id = "123456/?a="

    ## Fixtures
    @pytest.fixture
    def make_forms(self):
        """Create needed forms"""

        form1 = PollForm({
            "name": self.name1, 
            "question": self.question1, 
            "votable_mj": False, 
        })
        form2 = PollForm({
            "name": self.name2, 
            "question": self.question2, 
            "poll_type": self.type2, 
            "votable_mj": False,
            })

        return {"form1": form1, "form2": form2,}
    
    @pytest.fixture
    def create_user(self, django_user_model):
        username = "user1"
        password = "bar"
        user = django_user_model.objects.create_user(username=username, password=password)
        return user

    @pytest.mark.django_db
    def test_create_poll_runs(self, make_forms, create_user):
        """Simple test to check if creation does not crash (it runs)"""
    
        PollCreateService.create_or_edit_poll(make_forms["form1"], self.options1, user=create_user)
        

    @pytest.mark.django_db
    def test_create_poll_ok1(self, make_forms, create_user):
        """Check if object is created, aside with all options"""
    
        poll = PollCreateService.create_or_edit_poll(make_forms["form1"], self.options1, user=create_user)

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
    def test_create_missing_open_date(self, make_forms, create_user): 
        """Check what happen if I don't put open date"""

        poll = PollCreateService.create_or_edit_poll(make_forms["form1"], self.options1, create_user)
        assert_that(poll.open_datetime).is_none()

    @pytest.mark.django_db
    def test_create_w_open_date(self, make_forms, create_user): 
        """Check what happen if I insert open date"""

        form = make_forms["form1"]
        form.data["open_datetime"] = "31/12/2022 23:59"
        form.data["close_datetime"] = "31/12/2023 23:59"

        poll = PollCreateService.create_or_edit_poll(form, self.options1,create_user)

        assert_that(poll.open_datetime).is_instance_of(datetime.datetime)

        assert_that(poll.open_datetime.year).is_equal_to(2022)
        assert_that(poll.open_datetime.month).is_equal_to(12)
        assert_that(poll.open_datetime.day).is_equal_to(31)
        assert_that(poll.open_datetime.hour).is_equal_to(23)
        assert_that(poll.open_datetime.minute).is_equal_to(59)

    @pytest.mark.django_db
    def test_create_w_wrong_date(self, make_forms,create_user): 
        """Check what happen if I insert a bad open date
        (I expect an exception)"""

        form = make_forms["form1"]
        form.data["open_datetime"] = "31/13/2022 23:59"
        form.data["close_datetime"] = "31/12/2023 23:59"

        assert_that(PollCreateService.create_or_edit_poll) \
            .raises(PollMainDataNotValidException) \
            .when_called_with(poll_form=form, options=self.options1, user=create_user)

    @pytest.mark.django_db
    def test_create_without_close_date(self, make_forms,create_user): 
        """Check what happen if I don't insert a close date"""

        form = make_forms["form1"]
        form.data["open_datetime"] = "31/12/2022 23:59"

        assert_that(PollCreateService.create_or_edit_poll) \
            .raises(PollMainDataNotValidException) \
            .when_called_with(poll_form=form, options=self.options1,user=create_user)

    @pytest.mark.django_db
    def test_create_without_open_date(self, make_forms,create_user): 
        """Check what happen if I don't insert a open date"""

        form = make_forms["form1"]
        form.data["close_datetime"] = "31/12/2022 23:59"

        assert_that(PollCreateService.create_or_edit_poll) \
            .raises(PollMainDataNotValidException) \
            .when_called_with(poll_form=form, options=self.options1,user=create_user)

    @pytest.mark.django_db
    def test_create_with_precedent_close_dates(self, make_forms,create_user): 
        """Check what happen if I insert a open date after a close date"""

        form = make_forms["form1"]
        form.data["open_datetime"] = "31/12/2100 23:59"
        form.data["close_datetime"] = "31/12/2100 22:59"

        assert_that(PollCreateService.create_or_edit_poll) \
            .raises(PollMainDataNotValidException) \
            .when_called_with(poll_form=form, options=self.options1,user=create_user)

    @pytest.mark.django_db
    def test_create_missing_name(self, make_forms,create_user):
        """Check what happend if I don't insert name"""

        form = make_forms["form1"]
        form.data["name"] = " "

        assert_that(PollCreateService.create_or_edit_poll) \
            .raises(PollMainDataNotValidException) \
            .when_called_with(poll_form=form, options=self.options1,user=create_user)

    @pytest.mark.django_db
    def test_create_missing_question(self, make_forms,create_user):
        """Check what happend if I don't insert question"""

        form = make_forms["form1"]
        form.data["question"] = None

        assert_that(PollCreateService.create_or_edit_poll) \
            .raises(PollMainDataNotValidException) \
            .when_called_with(poll_form=form, options=self.options1,user=create_user)

    @pytest.mark.django_db
    def test_create_missing_closedate(self, make_forms,create_user):
        """Check what happend if I don't insert close date"""

        form = make_forms["form1"]
        form.data["close_datetime"] = " "

        assert_that(PollCreateService.create_or_edit_poll) \
            .raises(PollMainDataNotValidException) \
            .when_called_with(poll_form=form, options=self.options1,user=create_user)

    @pytest.mark.django_db
    def test_create_few_options_1(self, make_forms,create_user):
        """Check what happend if I don't insert enough options"""

        assert_that(PollCreateService.create_or_edit_poll) \
            .raises(TooFewOptionsException) \
            .when_called_with(poll_form=make_forms["form1"], options=self.options_few1,user=create_user)

    @pytest.mark.django_db
    def test_create_few_options_2(self, make_forms,create_user):
        """Check what happend if I don't insert enough options
        (ensuring empty space is not consiederd a valid option)"""

        assert_that(PollCreateService.create_or_edit_poll) \
            .raises(TooFewOptionsException) \
            .when_called_with(poll_form=make_forms["form1"], options=self.options_few2,user=create_user)

    @pytest.mark.django_db
    def test_create_too_many_options(self, make_forms,create_user):
        """Check what happend if I insert too many options"""

        assert_that(PollCreateService.create_or_edit_poll) \
            .raises(TooManyOptionsException) \
            .when_called_with(poll_form=make_forms["form1"], options=self.options_many,user=create_user)

    ## ------------------------------------
    ## Test Majoriry Judjment creation

    @pytest.mark.django_db
    def test_create_missing_type(self, make_forms,create_user):
        """Check what happend if I don't set type
        (I expect a classic single option poll)"""

        poll = PollCreateService.create_or_edit_poll(
            make_forms["form1"], 
            self.options1,user=create_user)

        assert_that(poll.poll_type).is_equal_to(PollModel.PollType.SINGLE_OPTION)


    @pytest.mark.django_db
    def test_create_majority_judjment(self, make_forms, create_user):
        """Create a majority judment poll and 
        ensure type is right"""

        poll = PollCreateService.create_or_edit_poll(
            make_forms["form2"], 
            self.options2,
            user=create_user)

        # ensure type is MajorityJudment
        assert_that(poll.poll_type).is_equal_to(self.type2)

    @pytest.mark.django_db
    def test_create_majority_judjment_few_options(self, make_forms,create_user):
        """A majority judment poll should have at least 2 options. 
        We try passing 1 and we expect an exception"""

        assert_that(PollCreateService.create_or_edit_poll) \
            .raises(TooFewOptionsException) \
            .when_called_with(
                poll_form=make_forms["form2"], 
                # pass just 1 options instead of 2
                options=self.options_few1,
                user=create_user)
        
    @pytest.mark.django_db
    def test_create_majority_judjment_few_options_2(self, make_forms,create_user):
        """A poll votable ALSO witn majority judment 
        should have at least 2 options. We try passing 1 and 
        we expect an exception"""

        # prepare a poll votable also w MJ but with 
        # only two options
        form = make_forms["form1"]
        form.data["votable_mj"] = True

        assert_that(PollCreateService.create_or_edit_poll) \
            .raises(TooFewOptionsException) \
            .when_called_with(
                poll_form=make_forms["form1"], 
                # pass just 1 options instead of 2
                options=self.options_few1,
                user=create_user)

    @pytest.mark.django_db
    def test_form_get_min_options(self, make_forms):
        """ensure form objects return correct number
        of min options foreach poll type"""

        assert_that(make_forms["form1"].get_min_options()).is_equal_to(2)
        #change in min options in mj since 14/03/2023
        assert_that(make_forms["form2"].get_min_options()).is_equal_to(2)

    @pytest.mark.django_db
    def test_form_get_type_verbose_name(self, make_forms):
        """ensure form objects return correct 
        verbose name forach poll type"""

        assert_that(make_forms["form1"].get_type_verbose_name()).is_equal_to("Opzione Singola")
        assert_that(make_forms["form2"].get_type_verbose_name()).is_equal_to("Giudizio Maggioritario")

    @pytest.mark.django_db
    def test_create_custom_short_id(self, make_forms, create_user): 
        """Ensure url code (short_id) can be costumized"""

        custom_short_id = "abcdef123456"
        
        form1 = make_forms["form1"]
        form1.data[SHORT_ID] = custom_short_id

        poll = PollCreateService.create_or_edit_poll(
            poll_form=form1, options=self.options1, user=create_user)

        assert_that(poll).is_instance_of(PollModel)
        assert_that(poll.short_id).is_equal_to(custom_short_id)

    @pytest.mark.django_db
    def test_create_too_short_short_id(self, make_forms, create_user): 
        """Ensure url code (short_id) is long enough"""

        form2 = make_forms["form2"]
        form2.data[SHORT_ID] = self.too_short_id

        assert_that(PollCreateService.create_or_edit_poll) \
            .raises(PollMainDataNotValidException) \
            .when_called_with(poll_form=form2, 
                              options=self.options2, 
                              user=create_user)
        
    @pytest.mark.django_db
    def test_create_missing_short_id(self, make_forms, create_user): 
        """Ensure url code (short_id) is given"""

        form2 = make_forms["form2"]
        form2.data[SHORT_ID] = None

        assert_that(PollCreateService.create_or_edit_poll) \
            .raises(PollMainDataNotValidException) \
            .when_called_with(poll_form=form2, 
                              options=self.options2, 
                              user=create_user)
        
    @pytest.mark.django_db
    def test_create_unvalid_short_id(self, make_forms, create_user): 
        """Ensure url code (short_id) is given"""

        form2 = make_forms["form2"]
        form2.data[SHORT_ID] = self.test_create_unvalid_short_id

        assert_that(PollCreateService.create_or_edit_poll) \
            .raises(PollMainDataNotValidException) \
            .when_called_with(poll_form=form2, 
                              options=self.options2, 
                              user=create_user)

    @pytest.mark.django_db
    def test_create_duplicate_short_id(self, make_forms, create_user): 
        """Ensure system does not permit creation of
        polls w duplicate url code (short_id)"""

        form1 = make_forms["form1"]
        form2 = make_forms["form2"]

        form1.data[SHORT_ID] = form2.data[SHORT_ID] = "123456"

        # first creation will be performed correctly
        assert_that(PollCreateService.create_or_edit_poll(
            poll_form=form1, options=self.options1, user=create_user)) \
            .is_instance_of(PollModel)
        
        # second creation will raise error
        assert_that(PollCreateService.create_or_edit_poll) \
            .raises(PollMainDataNotValidException) \
            .when_called_with(poll_form=form2, 
                              options=self.options2, 
                              user=create_user)
