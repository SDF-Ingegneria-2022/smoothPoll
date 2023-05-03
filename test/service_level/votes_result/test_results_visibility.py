from django.utils import timezone
from typing import List, Tuple
import pytest
from assertpy import assert_that
from apps.polls_management.exceptions.poll_cannot_be_closed_exception import PollCannotBeClosedException
from apps.polls_management.exceptions.poll_is_close_exception import PollIsCloseException
from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.services.poll_service import PollService

from test.service_level.utils.create_polls_utils import create_single_option_polls, get_user

class TestResultsVisibility:

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
            'user': get_user(django_user_model)
        }
    
    @pytest.mark.django_db
    def test_is_results_visible_voter(self, create_polls, django_user_model):
        """"""

        # set open and close date so polls are open now
        for k in create_polls.keys():
            create_polls[k].open_datetime = timezone.now() - timezone.timedelta(days=1)
            create_polls[k].close_datetime = timezone.now() + timezone.timedelta(days=1)
            create_polls[k].save()

        # check that some polls are closable and some not
        assert_that(create_polls['always_visible'].are_results_visible()).is_true()
        assert_that(create_polls['hidden_until_closed_for_all'].are_results_visible()).is_false()
        
        # check for voter side
        assert_that(create_polls['hidden_until_closed_for_voters'].are_results_visible()).is_false()
       
    def test_results_visible_author(self, create_polls, django_user_model):
        
        # set open and close date so polls are open now
        for k in create_polls.keys():
            create_polls[k].open_datetime = timezone.now() - timezone.timedelta(days=1)
            create_polls[k].close_datetime = timezone.now() + timezone.timedelta(days=1)
            create_polls[k].save()
            
        # User not author
        user_not_author = django_user_model.objects.create_user(username="user_not_author", password="password")
         
        # check for author side with right user
        assert_that(create_polls['hidden_until_closed_for_voters'].are_results_visible(create_polls['user'])).is_true()
        
        # check for author side with wrong user
        assert_that(create_polls['hidden_until_closed_for_voters'].are_results_visible(user_not_author)).is_false()
    
    def test_results_visible_with_closed_poll(self, create_polls):

        # set open and close date so polls are already closed
        for k in create_polls.keys():
            create_polls[k].open_datetime = timezone.now() - timezone.timedelta(days=2)
            create_polls[k].close_datetime = timezone.now() - timezone.timedelta(days=1)
            create_polls[k].save()

        # check that some polls are closable and some not
        assert_that(create_polls['always_visible'].are_results_visible()).is_true()
        assert_that(create_polls['hidden_until_closed_for_all'].are_results_visible()).is_true()
        assert_that(create_polls['hidden_until_closed_for_voters'].are_results_visible()).is_true()