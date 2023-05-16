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

    @pytest.mark.django_db
    def test_schulze_vote_creation(self, test_polls):
        """Check if schulze vote model is created"""

        poll1: PollModel = test_polls['poll_case_23']
        
        schulze1: SchulzeVoteModel = SchulzeVoteModel(poll=poll1)

        input1: List[int] = []
        input_obj: List[PollOptionModel] = list(PollOptionModel.objects.filter(poll_fk=poll1).order_by('id'))
        for i in input_obj:
            input1.append(i.id)

        # print(input1)

        schulze1.set_order(input1)
        schulze1.save()

        assert_that(schulze1.order).is_equal_to("12,13,14,15,16")
        test_order = schulze1.get_order()
        assert_that(test_order).is_equal_to(["12", "13", "14", "15", "16"])

        input_mismatch: List[int] = [1, 2, 3]
        input_repeat: List[int] = [1, 2, 3, 3, 5]

        assert_that(schulze1.set_order) \
            .raises(PollOptionNumberMismatch) \
            .when_called_with(input_mismatch)
        
        input_not_exist: List[int] = [30, 2, 3, 4, 5]

        assert_that(schulze1.set_order) \
            .raises(PollOptionDoesNotExist) \
            .when_called_with(input_not_exist)
        
        wrong_input: List[int] = [1, 2, 3, 4, 6]

        assert_that(schulze1.set_order) \
            .raises(WrongPollOptions) \
            .when_called_with(wrong_input)

