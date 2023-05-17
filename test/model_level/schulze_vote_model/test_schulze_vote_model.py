from typing import List
import pytest
from apps.polls_management.exceptions.poll_option_model_does_not_exist_exception import PollOptionDoesNotExist
from apps.polls_management.exceptions.poll_option_number_mismatch_exception import PollOptionNumberMismatch
from apps.polls_management.exceptions.wrong_poll_options_exception import WrongPollOptions
from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.models.poll_option_model import PollOptionModel
from apps.polls_management.models.schulze_vote_model import SchulzeVoteModel
from test.service_level.utils.has_test_polls import HasTestPolls
from assertpy import assert_that

class TestSchulzeVoteModel(HasTestPolls):
    pass
    # check methods of schulze vote model ----------------------------------------------

    # @pytest.mark.django_db
    # def test_schulze_vote_creation(self, test_polls):
    #     """Check if schulze vote model is created"""

    #     poll_test: PollModel = test_polls['poll_case_23']
        
    #     schulze: SchulzeVoteModel = SchulzeVoteModel(poll=poll_test)

    #     # poll options ids for poll_test are 12,13,14,15,16

    #     # first test input ********************************

    #     input1: List[int] = [14, 13, 12, 15, 16]

    #     schulze.set_order(input1)
    #     schulze.save()
    #     assert_that(schulze.order).is_equal_to("14,13,12,15,16")

    #     test_order = schulze.get_order()
    #     assert_that(test_order).is_equal_to(["14", "13", "12", "15", "16"])

    #     list_options = schulze.get_order_as_ids()
    #     assert_that(list_options).is_equal_to(["12", "13", "14", "15", "16"])

    #     # second test input ********************************

    #     input2: List[int] = [12, 13, 14, 15, 16]

    #     schulze.set_order(input2)
    #     schulze.save()
    #     assert_that(schulze.order).is_equal_to("12,13,14,15,16")

    #     test_order = schulze.get_order()
    #     assert_that(test_order).is_equal_to(["12", "13", "14", "15", "16"])

    #     list_options = schulze.get_order_as_ids()
    #     assert_that(list_options).is_equal_to(["12", "13", "14", "15", "16"])

    #     # third test input ********************************

    #     input3: List[int] = [16, 13, 15, 14, 12]

    #     schulze.set_order(input3)
    #     schulze.save()
    #     assert_that(schulze.order).is_equal_to("16,13,15,14,12")

    #     test_order = schulze.get_order()
    #     assert_that(test_order).is_equal_to(["16", "13", "15", "14", "12"])

    #     list_options = schulze.get_order_as_ids()
    #     assert_that(list_options).is_equal_to(["12", "13", "14", "15", "16"])


    #     test_options_as_obj: List[PollOptionModel] = list(PollOptionModel.objects.filter(poll_fk=poll_test).order_by('id'))
    #     list_options_as_obj: List[PollOptionModel] = schulze.get_order_as_obj()
    #     assert_that(list_options_as_obj).is_equal_to(test_options_as_obj)

    # # check exceptions -----------------------------------------------------------------

    # @pytest.mark.django_db
    # def test_schulze_vote_exceptions(self, test_polls):
    #     """Check raised exceptions for schulze vote model"""

    #     poll_test: PollModel = test_polls['poll_case_23']
        
    #     schulze: SchulzeVoteModel = SchulzeVoteModel(poll=poll_test)

    #     # poll options ids for poll_test are now 17,18,19,20,21

    #     input_mismatch: List[int] = [17, 18, 19]

    #     assert_that(schulze.set_order) \
    #         .raises(PollOptionNumberMismatch) \
    #         .when_called_with(input_mismatch)
        
    #     input_not_exist: List[int] = [1, 17, 18, 19, 20]

    #     assert_that(schulze.set_order) \
    #         .raises(PollOptionDoesNotExist) \
    #         .when_called_with(input_not_exist)
        
    #     wrong_input: List[int] = [17, 18, 19, 20, 22]

    #     assert_that(schulze.set_order) \
    #         .raises(WrongPollOptions) \
    #         .when_called_with(wrong_input)