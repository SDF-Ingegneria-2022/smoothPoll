from django.utils import timezone
from typing import List, Tuple
import pytest
from assertpy import assert_that
from apps.polls_management.exceptions.poll_cannot_be_closed_exception import PollCannotBeClosedException
from apps.polls_management.exceptions.poll_is_close_exception import PollIsCloseException
from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.services.poll_service import PollService

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
            create_polls[k].open_datetime = timezone.now() - timezone.timedelta(days=1)
            create_polls[k].close_datetime = timezone.now() + timezone.timedelta(days=1)
            create_polls[k].save()

        # check that some polls are closable and some not
        assert_that(create_polls['always_visible'].is_closable_now()).is_true()
        assert_that(create_polls['hidden_until_closed_for_all'].is_closable_now()).is_true()
        assert_that(create_polls['hidden_until_closed_for_voters'].is_closable_now()).is_false()

    def test_non_open_polls_cannot_be_closed(self, create_polls):


        # set open and close date so polls are not yet open
        for k in create_polls.keys():
            create_polls[k].open_datetime = timezone.now() + timezone.timedelta(days=1)
            create_polls[k].close_datetime = timezone.now() + timezone.timedelta(days=2)
            create_polls[k].save()

        # check that some polls are closable and some not
        assert_that(create_polls['always_visible'].is_closable_now()).is_false()
        assert_that(create_polls['hidden_until_closed_for_all'].is_closable_now()).is_false()
        assert_that(create_polls['hidden_until_closed_for_voters'].is_closable_now()).is_false()

    def test_closed_polls_cannot_be_closed(self, create_polls):

        # set open and close date so polls are already closed
        for k in create_polls.keys():
            create_polls[k].open_datetime = timezone.now() - timezone.timedelta(days=2)
            create_polls[k].close_datetime = timezone.now() - timezone.timedelta(days=1)
            create_polls[k].save()

        # check that some polls are closable and some not
        assert_that(create_polls['always_visible'].is_closable_now()).is_false()
        assert_that(create_polls['hidden_until_closed_for_all'].is_closable_now()).is_false()
        assert_that(create_polls['hidden_until_closed_for_voters'].is_closable_now()).is_false()

        # ====== Close poll anytime ======
    
    @pytest.mark.django_db
    def test_close_poll(self, create_polls):
        """Test close poll"""
        
        # set open and close date so polls are open now
        for k in create_polls.keys():

            create_polls[k].open_datetime = timezone.now() - timezone.timedelta(days=1)
            create_polls[k].close_datetime = timezone.now() + timezone.timedelta(days=1)
            create_polls[k].save()

        # check those polls can be closed
        PollService.close_poll(create_polls["always_visible"].id)
        create_polls["always_visible"].refresh_from_db()
        assert_that(create_polls["always_visible"].is_closed()).is_true()

        PollService.close_poll(create_polls["hidden_until_closed_for_all"].id)
        create_polls["hidden_until_closed_for_all"].refresh_from_db()
        assert_that(create_polls["hidden_until_closed_for_all"].is_closed()).is_true()

        # check some polls instead cannot be closed
        assert_that(PollService.close_poll) \
            .raises(PollCannotBeClosedException) \
            .when_called_with(create_polls["hidden_until_closed_for_voters"].id)

    @pytest.mark.django_db
    def test_close_poll_already_closed(self, create_polls):
        """Test close poll, poll already closed"""

        # set open and close date so polls are already closed
        for k in create_polls.keys():
            create_polls[k].open_datetime = timezone.now() - timezone.timedelta(days=2)
            create_polls[k].close_datetime = timezone.now() - timezone.timedelta(days=1)
            create_polls[k].save()

        # check none of the polls can be closed again
        assert_that(PollService.close_poll) \
            .raises(PollIsCloseException) \
            .when_called_with(id=create_polls["always_visible"].id)
        assert_that(PollService.close_poll) \
            .raises(PollIsCloseException) \
            .when_called_with(id=create_polls["hidden_until_closed_for_all"].id)
        assert_that(PollService.close_poll) \
            .raises(PollIsCloseException) \
            .when_called_with(id=create_polls["hidden_until_closed_for_voters"].id)

    @pytest.mark.django_db
    def test_close_poll_not_open(self, create_polls):
        """Test close poll, poll that need to be opened"""
        
        # set open and close date so polls are not yet open
        for k in create_polls.keys():
            create_polls[k].open_datetime = timezone.now() + timezone.timedelta(days=1)
            create_polls[k].close_datetime = timezone.now() + timezone.timedelta(days=2)
            create_polls[k].save()

        # check none of the polls can be closed before opening
        assert_that(PollService.close_poll) \
            .raises(PollCannotBeClosedException) \
            .when_called_with(id=create_polls["always_visible"].id)
        assert_that(PollService.close_poll) \
            .raises(PollCannotBeClosedException) \
            .when_called_with(id=create_polls["hidden_until_closed_for_all"].id)
        assert_that(PollService.close_poll) \
            .raises(PollCannotBeClosedException) \
            .when_called_with(id=create_polls["hidden_until_closed_for_voters"].id)


