from typing import List
from django.urls import reverse
import pytest
from assertpy import assert_that
from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.models.poll_token import PollTokens
from test.service_level.utils.create_polls_utils import create_single_option_polls
from apps.polls_management.services.poll_token_service import PollTokenService

class TestPollTokenService():
    """Tests related to token service level."""

    @pytest.fixture()
    def create_polls(request, django_user_model):
        """Fixture for creating polls."""
        create_single_option_polls(django_user_model, number_of_polls=1)

    @pytest.mark.django_db
    def test_create_tokens_for_poll(self, create_polls):
        """Test used to create and verify tokens."""

        poll_list: List[PollModel] = PollModel.objects.all()
        poll: PollModel = poll_list[0]
        host: str = "http://127.0.0.1:8000"
        link: str = host + reverse('apps.votes_results:vote', 
            args=(poll.id,))

        PollTokenService.create_tokens(link, 10, poll)

        token_list: List[PollTokens] = PollTokens.objects.filter(poll_fk=poll)

        assert_that(token_list).is_length(10)

        for token in token_list:
            assert_that(token).is_instance_of(PollTokens)
            assert_that(token.token_user).is_not_none()
            assert_that(token.majority_use).is_false()
            assert_that(token.single_option_use).is_false()

    @pytest.mark.django_db
    def test_tokens_bools(self, create_polls):
        """Test if token bools are correctly handled."""

        poll_list: List[PollModel] = PollModel.objects.all()
        poll: PollModel = poll_list[0]
        host: str = "http://127.0.0.1:8000"
        link: str = host + reverse('apps.votes_results:vote', 
            args=(poll.id,))

        PollTokenService.create_tokens(link, 10, poll)

        token_list: List[PollTokens] = PollTokens.objects.filter(poll_fk=poll)

        for token in token_list:
            assert_that(PollTokenService.is_single_option_token_used(token)).is_false()
            assert_that(PollTokenService.is_majority_token_used(token)).is_false()
            PollTokenService.check_majority_option(token)
            assert_that(PollTokenService.is_majority_token_used(token)).is_true()
            PollTokenService.check_single_option(token)
            assert_that(PollTokenService.is_single_option_token_used(token)).is_true()   

    @pytest.mark.django_db
    def test_available_and_unavailable_tokens(self, create_polls):
        """Test if available and unavailable token lists are returned correctly."""

        poll_list: List[PollModel] = PollModel.objects.all()
        poll: PollModel = poll_list[0]
        host: str = "http://127.0.0.1:8000"
        link: str = host + reverse('apps.votes_results:vote', 
            args=(poll.id,))

        PollTokenService.create_tokens(link, 10, poll)

        token_list: List[PollTokens] = PollTokens.objects.filter(poll_fk=poll)

        PollTokenService.check_single_option(token_list[0])

        assert_that(PollTokenService.available_token_list(poll)).is_length(9)
        assert_that(PollTokenService.unavailable_token_list(poll)).is_length(1)

        PollTokenService.check_majority_option(token_list[0])

        assert_that(PollTokenService.available_token_list(poll)).is_length(9)
        assert_that(PollTokenService.unavailable_token_list(poll)).is_length(1)

        PollTokenService.check_majority_option(token_list[1])

        assert_that(PollTokenService.available_token_list(poll)).is_length(8)
        assert_that(PollTokenService.unavailable_token_list(poll)).is_length(2)

        PollTokenService.check_majority_option(token_list[2])

        assert_that(PollTokenService.available_token_list(poll)).is_length(7)
        assert_that(PollTokenService.unavailable_token_list(poll)).is_length(3)

        PollTokenService.check_single_option(token_list[2])

        assert_that(PollTokenService.available_token_list(poll)).is_length(7)
        assert_that(PollTokenService.unavailable_token_list(poll)).is_length(3)


        


