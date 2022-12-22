from apps.polls_management.classes.poll_form import PollForm
from polls.models.poll_model import PollModel
from polls.models.poll_option_model import PollOptionModel
from apps.polls_management.services.poll_create_service import PollCreateService
from apps.polls_management.exceptions.poll_not_valid_creation_exception import *

from typing import List
import pytest
from assertpy import assert_that


class TestPollEdit:
    """Test suite that covers all methods in the PollService class"""

    name1: str = "Sondaggio cibo pt. 2"
    question1: str = "Ti piace la pizza?"
    options1: List[str] = ["Si", "No",]
    options2: List[str] = ["Si", "No", "Forse",]
    options3: List[str] = ["Si", "No", "Forse", "Potrebbe",]

    name2: str = "Sondaggio cibo pt. 2"
    question2: str = "Qual è il tuo cibo preferito?"
    options4: List[str] = ["Pizza", "Pasta", "Carne", "Pesce", "Altro", ]
    type2: str = PollModel.PollType.MAJORITY_JUDJMENT

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
    def test_edit_poll_runs(self, make_forms):
        """Simple test to check if edit after creation does not crash (it runs)"""
    
        PollCreateService.create_or_edit_poll(make_forms["form1"], self.options1)

        PollCreateService.create_or_edit_poll(make_forms["form1"], self.options2)

        PollCreateService.create_or_edit_poll(make_forms["form2"], self.options4)
        

    @pytest.mark.django_db
    def test_edit_poll_ok1(self, make_forms):
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
        # in this case we edit the poll adding an option
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

    @pytest.mark.django_db
    def test_edit_poll_ok2(self, make_forms):
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
        # in this case we edit the poll adding two options
        poll2 = PollCreateService.create_or_edit_poll(make_forms["form1"], self.options3)

        # check it has been edited correctly
        assert_that(PollModel.objects.get(id=poll2.id)).is_equal_to(poll)
        assert_that(poll2.id).is_equal_to(poll.id)

        # check each options have been saved correctly
        assert_that(PollOptionModel.objects.filter(poll_fk=poll2).count()).is_equal_to(self.options3.__len__())
        assert_that(poll.options().__len__()).is_equal_to(self.options3.__len__())

        # assert that all and only the input passed options are returned
        options_to_search = self.options3.copy()
        for o in poll2.options():
            assert_that(o.value in options_to_search).is_true()
            options_to_search.remove(o.value)

        assert_that(options_to_search.__len__()).is_equal_to(0)

    @pytest.mark.django_db
    def test_edit_poll_ok3(self, make_forms):
        """Check if object is edited, aside with all correct options"""
    
        poll = PollCreateService.create_or_edit_poll(make_forms["form1"], self.options3)

        # check data 
        assert_that(poll).is_instance_of(PollModel)
        assert_that(poll.name).is_equal_to(self.name1)
        assert_that(poll.question).is_equal_to(self.question1)

        # check it has been saved correctly
        assert_that(PollModel.objects.get(id=poll.id)).is_equal_to(poll)

        # check each options have been saved correctly
        assert_that(PollOptionModel.objects.filter(poll_fk=poll).count()).is_equal_to(self.options3.__len__())
        assert_that(poll.options().__len__()).is_equal_to(self.options3.__len__())

        # assert that all and only the input passed options are returned
        options_to_search = self.options3.copy()
        for o in poll.options():
            assert_that(o.value in options_to_search).is_true()
            options_to_search.remove(o.value)

        assert_that(options_to_search.__len__()).is_equal_to(0)

        # now check that edit works as expected
        # in this case we edit the poll deleting two options
        poll2 = PollCreateService.create_or_edit_poll(make_forms["form1"], self.options1)

        # check it has been edited correctly
        assert_that(PollModel.objects.get(id=poll2.id)).is_equal_to(poll)
        assert_that(poll2.id).is_equal_to(poll.id)

        # check each options have been saved correctly
        assert_that(PollOptionModel.objects.filter(poll_fk=poll2).count()).is_equal_to(self.options1.__len__())
        assert_that(poll.options().__len__()).is_equal_to(self.options1.__len__())

        # assert that all and only the input passed options are returned
        options_to_search = self.options1.copy()
        for o in poll2.options():
            assert_that(o.value in options_to_search).is_true()
            options_to_search.remove(o.value)

        assert_that(options_to_search.__len__()).is_equal_to(0)

    @pytest.mark.django_db
    def test_edit_poll_ok4(self, make_forms):
        """Check if object is edited, (majority poll case) aside with all correct options"""
    
        poll = PollCreateService.create_or_edit_poll(make_forms["form2"], self.options4)

        # check data 
        assert_that(poll).is_instance_of(PollModel)
        assert_that(poll.name).is_equal_to(self.name2)
        assert_that(poll.question).is_equal_to(self.question2)
        assert_that(poll.poll_type).is_equal_to(self.type2)

        # check it has been saved correctly
        assert_that(PollModel.objects.get(id=poll.id)).is_equal_to(poll)

        # check each options have been saved correctly
        assert_that(PollOptionModel.objects.filter(poll_fk=poll).count()).is_equal_to(self.options4.__len__())
        assert_that(poll.options().__len__()).is_equal_to(self.options4.__len__())

        # assert that all and only the input passed options are returned
        options_to_search = self.options4.copy()
        for o in poll.options():
            assert_that(o.value in options_to_search).is_true()
            options_to_search.remove(o.value)

        assert_that(options_to_search.__len__()).is_equal_to(0)

        # now check that edit works as expected
        # in this case we edit the poll deleting two options
        poll2 = PollCreateService.create_or_edit_poll(make_forms["form2"], self.options3)

        # check it has been edited correctly
        assert_that(PollModel.objects.get(id=poll2.id)).is_equal_to(poll)
        assert_that(poll2.id).is_equal_to(poll.id)

        # check each options have been saved correctly
        assert_that(PollOptionModel.objects.filter(poll_fk=poll2).count()).is_equal_to(self.options3.__len__())
        assert_that(poll.options().__len__()).is_equal_to(self.options3.__len__())

        # assert that all and only the input passed options are returned
        options_to_search = self.options3.copy()
        for o in poll2.options():
            assert_that(o.value in options_to_search).is_true()
            options_to_search.remove(o.value)

        assert_that(options_to_search.__len__()).is_equal_to(0)

    @pytest.mark.django_db
    def test_edit_poll_ok5(self, make_forms):
        """Check if object is edited, (majority poll case) aside with all correct options"""
    
        poll = PollCreateService.create_or_edit_poll(make_forms["form2"], self.options2)

        # check data 
        assert_that(poll).is_instance_of(PollModel)
        assert_that(poll.name).is_equal_to(self.name2)
        assert_that(poll.question).is_equal_to(self.question2)
        assert_that(poll.poll_type).is_equal_to(self.type2)

        # check it has been saved correctly
        assert_that(PollModel.objects.get(id=poll.id)).is_equal_to(poll)

        # check each options have been saved correctly
        assert_that(PollOptionModel.objects.filter(poll_fk=poll).count()).is_equal_to(self.options2.__len__())
        assert_that(poll.options().__len__()).is_equal_to(self.options2.__len__())

        # assert that all and only the input passed options are returned
        options_to_search = self.options2.copy()
        for o in poll.options():
            assert_that(o.value in options_to_search).is_true()
            options_to_search.remove(o.value)

        assert_that(options_to_search.__len__()).is_equal_to(0)

        # now check that edit works as expected
        # in this case we edit the poll deleting two options
        poll2 = PollCreateService.create_or_edit_poll(make_forms["form2"], self.options4)

        # check it has been edited correctly
        assert_that(PollModel.objects.get(id=poll2.id)).is_equal_to(poll)
        assert_that(poll2.id).is_equal_to(poll.id)

        # check each options have been saved correctly
        assert_that(PollOptionModel.objects.filter(poll_fk=poll2).count()).is_equal_to(self.options4.__len__())
        assert_that(poll.options().__len__()).is_equal_to(self.options4.__len__())

        # assert that all and only the input passed options are returned
        options_to_search = self.options4.copy()
        for o in poll2.options():
            assert_that(o.value in options_to_search).is_true()
            options_to_search.remove(o.value)

        assert_that(options_to_search.__len__()).is_equal_to(0)

    # @pytest.mark.django_db
    # def test_edit_poll_ok6(self, make_forms):
    #     """Check if object is edited, (from single option to majority) aside with all correct options"""
    
    #     poll = PollCreateService.create_or_edit_poll(make_forms["form1"], self.options1)

    #     # check data 
    #     assert_that(poll).is_instance_of(PollModel)
    #     assert_that(poll.name).is_equal_to(self.name1)
    #     assert_that(poll.question).is_equal_to(self.question1)

    #     # check it has been saved correctly
    #     assert_that(PollModel.objects.get(id=poll.id)).is_equal_to(poll)

    #     # check each options have been saved correctly
    #     assert_that(PollOptionModel.objects.filter(poll_fk=poll).count()).is_equal_to(self.options1.__len__())
    #     assert_that(poll.options().__len__()).is_equal_to(self.options1.__len__())

    #     # assert that all and only the input passed options are returned
    #     options_to_search = self.options1.copy()
    #     for o in poll.options():
    #         assert_that(o.value in options_to_search).is_true()
    #         options_to_search.remove(o.value)

    #     assert_that(options_to_search.__len__()).is_equal_to(0)

    #     # now check that edit works as expected
    #     # in this case we edit the poll deleting two options
    #     poll2 = PollCreateService.create_or_edit_poll(make_forms["form2"], self.options4)

    #     # check data 
    #     assert_that(poll2).is_instance_of(PollModel)
    #     assert_that(poll2.name).is_equal_to(self.name2)
    #     assert_that(poll2.question).is_equal_to(self.question2)
    #     assert_that(poll2.poll_type).is_equal_to(self.type2)

    #     # check it has been edited correctly
    #     assert_that(PollModel.objects.get(id=poll2.id)).is_equal_to(poll)
    #     assert_that(poll2.id).is_equal_to(poll.id)

    #     # check each options have been saved correctly
    #     assert_that(PollOptionModel.objects.filter(poll_fk=poll2).count()).is_equal_to(self.options4.__len__())
    #     assert_that(poll.options().__len__()).is_equal_to(self.options4.__len__())

    #     # assert that all and only the input passed options are returned
    #     options_to_search = self.options4.copy()
    #     for o in poll2.options():
    #         assert_that(o.value in options_to_search).is_true()
    #         options_to_search.remove(o.value)

    #     assert_that(options_to_search.__len__()).is_equal_to(0)

