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

    # check methods of schulze vote model ----------------------------------------------

    @pytest.mark.django_db
    def test_schulze_vote_creation(self, test_polls):
        """Check if schulze vote model is created"""

        poll_test: PollModel = test_polls['poll_case_23']
        
        schulze: SchulzeVoteModel = SchulzeVoteModel(poll=poll_test)

        # first test input ********************************

        op4 = poll_test.options()[4].id
        op3 = poll_test.options()[3].id
        op2 = poll_test.options()[2].id
        op1 = poll_test.options()[1].id
        op0 = poll_test.options()[0].id

        input1: List[int] = [op4, op3, op2, op1, op0]

        schulze.set_order(input1)
        schulze.save()
        assert_that(schulze.order).is_equal_to(f"{op4},{op3},{op2},{op1},{op0}")

        test_order = schulze.get_order()
        assert_that(test_order).is_equal_to([str(op4), str(op3), str(op2), str(op1), str(op0)])

        list_options = schulze.get_order_as_ids()
        assert_that(list_options).is_equal_to([str(op0), str(op1), str(op2), str(op3), str(op4)])

        test_options_as_obj: List[PollOptionModel] = [poll_test.options()[4], \
                                                    poll_test.options()[3], \
                                                    poll_test.options()[2], \
                                                    poll_test.options()[1], \
                                                    poll_test.options()[0]]
        
        list_options_as_obj: List[PollOptionModel] = schulze.get_order_as_obj()
        assert_that(list_options_as_obj).is_equal_to(test_options_as_obj)

        # second test input ********************************

        input2: List[int] = [op2, op3, op1, op4, op0]

        schulze.set_order(input2)
        schulze.save()
        assert_that(schulze.order).is_equal_to(f"{op2},{op3},{op1},{op4},{op0}")

        test_order = schulze.get_order()
        assert_that(test_order).is_equal_to([str(op2), str(op3), str(op1), str(op4), str(op0)])

        list_options = schulze.get_order_as_ids()
        assert_that(list_options).is_equal_to([str(op0), str(op1), str(op2), str(op3), str(op4)])

        test_options_as_obj: List[PollOptionModel] = [poll_test.options()[2], \
                                                    poll_test.options()[3], \
                                                    poll_test.options()[1], \
                                                    poll_test.options()[4], \
                                                    poll_test.options()[0]]
        
        list_options_as_obj: List[PollOptionModel] = schulze.get_order_as_obj()
        assert_that(list_options_as_obj).is_equal_to(test_options_as_obj)

        # # third test input ********************************

        input3: List[int] = [op0, op1, op2, op3, op4]

        schulze.set_order(input3)
        schulze.save()
        assert_that(schulze.order).is_equal_to(f"{op0},{op1},{op2},{op3},{op4}")

        test_order = schulze.get_order()
        assert_that(test_order).is_equal_to([str(op0), str(op1), str(op2), str(op3), str(op4)])

        list_options = schulze.get_order_as_ids()
        assert_that(list_options).is_equal_to([str(op0), str(op1), str(op2), str(op3), str(op4)])


        test_options_as_obj: List[PollOptionModel] = [poll_test.options()[0], \
                                                    poll_test.options()[1], \
                                                    poll_test.options()[2], \
                                                    poll_test.options()[3], \
                                                    poll_test.options()[4]]
        
        list_options_as_obj: List[PollOptionModel] = schulze.get_order_as_obj()
        assert_that(list_options_as_obj).is_equal_to(test_options_as_obj)

    # check exceptions -----------------------------------------------------------------

    @pytest.mark.django_db
    def test_schulze_vote_exceptions(self, test_polls):
        """Check raised exceptions for schulze vote model"""

        poll_test: PollModel = test_polls['poll_case_23']
        wrong_poll: PollModel = test_polls['poll_case_1']
        
        schulze: SchulzeVoteModel = SchulzeVoteModel(poll=poll_test)

        op4 = poll_test.options()[4].id
        op3 = poll_test.options()[3].id
        op2 = poll_test.options()[2].id
        op1 = poll_test.options()[1].id
        op0 = poll_test.options()[0].id

        input_mismatch: List[int] = [op0, op1, op2]

        assert_that(schulze.set_order) \
            .raises(PollOptionNumberMismatch) \
            .when_called_with(input_mismatch)
        
        deleted_poll_option: PollOptionModel = PollOptionModel(value="Opzione cancellata", poll_fk=wrong_poll)
        deleted_poll_option.save()
        deleted_id: int = deleted_poll_option.id
        deleted_poll_option.delete()

        input_not_exist: List[int] = [deleted_id, op0, op1, op2, op3]

        assert_that(schulze.set_order) \
            .raises(PollOptionDoesNotExist) \
            .when_called_with(input_not_exist)
        
        wrong_poll_option: PollOptionModel = PollOptionModel(value="Opzione sbagliata", poll_fk=wrong_poll)
        wrong_poll_option.save()
        wpo_id: int = wrong_poll_option.id

        wrong_input: List[int] = [op0, op1, op2, op3, wpo_id]

        assert_that(schulze.set_order) \
            .raises(WrongPollOptions) \
            .when_called_with(wrong_input)