from django.urls import reverse
import pytest
from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.services.poll_token_service import PollTokenService
from test.service_level.utils.create_polls_utils import create_single_option_polls
from test.view_level.vote_process.test_render_vote_generic import TestRenderVoteGeneric


class TestRenderVoteMJ(TestRenderVoteGeneric):

    @pytest.fixture
    def create_poll(self, django_user_model):
        poll = create_single_option_polls(django_user_model, number_of_polls=1)[0]
        poll.poll_type = PollModel.PollType.MAJORITY_JUDJMENT
        poll.save()

        return poll

    @pytest.fixture
    def test_config(self, create_poll):
        return {
            "vote_page_url": reverse(
                'apps.votes_results:majority_judgment_vote', args=(create_poll.id,)), 
            "short_id_url": "/" + create_poll.short_id,
            "generic_vote_url": reverse('apps.votes_results:vote', args=(create_poll.id,)),

            "vote_page_template": "votes_results/majority_judgment_vote.html", 
            "poll_not_yet_open_template": "votes_results/poll_details.html", 
            "poll_closed_template": "votes_results/poll_details.html", 
            "insert_token_template": "polls_management/token_poll_redirect.html", 
            "make_auth_template": "global/login.html",    
        }
    
    @pytest.mark.django_db
    def test_config_has_everything(self, test_config):
        self._test_config_has_everything(test_config)
    
    @pytest.mark.django_db
    def test_render_vote_page(self, client, create_poll, test_config):
        self._test_render_vote_page(client, create_poll, test_config)

    @pytest.mark.django_db
    def test_not_yet_open_poll_page(self, client, create_poll, test_config):
        self._test_not_yet_open_poll_page(client, create_poll, test_config)

    @pytest.mark.django_db
    def test_generic_vote_redirect(self, client, create_poll, test_config):
        self._test_generic_vote_redirect(client, create_poll, test_config)

    @pytest.mark.django_db
    def test_short_id_redirect(self, client, create_poll, test_config):
        self._test_short_id_redirect(client, create_poll, test_config)

    @pytest.mark.django_db
    def test_render_vote_page_w_token(self, client, create_poll, test_config):
        self._test_render_vote_page_w_token(client, create_poll, test_config)

    @pytest.mark.django_db
    def test_missing_token(self, client, create_poll, test_config):
        self._test_missing_token(client, create_poll, test_config)

    @pytest.mark.django_db
    def test_wrong_token(self, client, create_poll, test_config):
        self._test_wrong_token(client, create_poll, test_config)

    @pytest.mark.django_db
    def test_used_token(self, client, create_poll, test_config):
        self._test_used_token(client, create_poll, test_config)

    @pytest.mark.django_db
    def test_vote_w_google_from_short_id(self, auth_client, create_poll, test_config):
        self._test_vote_w_google_from_short_id(auth_client, create_poll, test_config)

    @pytest.mark.django_db
    def test_vote_w_google_from_generic(self, auth_client, create_poll, test_config):
        self._test_vote_w_google_from_generic(auth_client, create_poll, test_config)

    @pytest.mark.django_db
    def test_try_vote_google_unauth(self, client, create_poll, test_config):
        self._test_try_vote_google_unauth(client, create_poll, test_config)

    @pytest.mark.django_db
    def test_try_vote_google_2_times(self, auth_client, create_poll, test_config):
        self._test_try_vote_google_2_times(auth_client, create_poll, test_config)