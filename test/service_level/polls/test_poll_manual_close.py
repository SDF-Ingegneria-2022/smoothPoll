from django.utils import timezone
from typing import List, Tuple
import pytest
from assertpy import assert_that
from apps.polls_management.models.poll_model import PollModel

from test.service_level.utils.create_polls_utils import create_single_option_polls

class TestPollManualClose:

    @pytest.fixture
    def create_polls(self, django_user_model):
        return {
            'always_visible': create_single_option_polls(
                django_user_model, 
                number_of_polls=1, 
                results_visibility=PollModel.PollResultsVisibility.ALWAYS_VISIBLE
                )[0],

            'hidden_until_closed_for_all': create_single_option_polls(
                django_user_model,
                number_of_polls=1,
                results_visibility=PollModel.PollResultsVisibility.HIDDEN_UNTIL_CLOSED_FOR_ALL
                )[0],

            'hidden_until_closed_for_voters': create_single_option_polls(
                django_user_model,
                number_of_polls=1,
                results_visibility=PollModel.PollResultsVisibility.HIDDEN_UNTIL_CLOSED_FOR_VOTERS
                )[0],
        }
    

    @pytest.mark.django_db
    def test_is_closable_policies(self, create_polls):
        """"""

        # set open and close date so polls are open now
        for k in create_polls.keys():
            create_polls[k].open_datetime = timezone.now()
            create_polls[k].close_datetime = timezone.now() + timezone.timedelta(days=1)
            create_polls[k].save()

        # check that some polls are closable and some not
        assert_that(create_polls['always_visible'].is_closable_now()).is_true()
        assert_that(create_polls['hidden_until_closed_for_all'].is_closable_now()).is_true()
        assert_that(create_polls['hidden_until_closed_for_voters'].is_closable_now()).is_false()

    def test_non_open_polls_cannot_be_closed(self, create_polls):


        # set open and close date so polls are open now
        for k in create_polls.keys():
            create_polls[k].open_datetime = timezone.now() + timezone.timedelta(days=1)
            create_polls[k].close_datetime = timezone.now() + timezone.timedelta(days=2)
            create_polls[k].save()

        # check that some polls are closable and some not
        assert_that(create_polls['always_visible'].is_closable_now()).is_false()
        assert_that(create_polls['hidden_until_closed_for_all'].is_closable_now()).is_false()
        assert_that(create_polls['hidden_until_closed_for_voters'].is_closable_now()).is_false()

    def test_closed_polls_cannot_be_closed(self, create_polls):

        # set open and close date so polls are open now
        for k in create_polls.keys():
            create_polls[k].open_datetime = timezone.now() - timezone.timedelta(days=1)
            create_polls[k].close_datetime = timezone.now()
            create_polls[k].save()

        # check that some polls are closable and some not
        assert_that(create_polls['always_visible'].is_closable_now()).is_false()
        assert_that(create_polls['hidden_until_closed_for_all'].is_closable_now()).is_false()
        assert_that(create_polls['hidden_until_closed_for_voters'].is_closable_now()).is_false()