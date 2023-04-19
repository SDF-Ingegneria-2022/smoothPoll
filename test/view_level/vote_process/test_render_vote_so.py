from django.urls import reverse
import pytest
from test.view_level.vote_process.test_render_vote_generic import TestRenderVoteGeneric


class TestRenderVoteSO(TestRenderVoteGeneric):

    @pytest.fixture
    def test_config(self, create_poll):
        return {
            "vote_page_url": reverse(
                'apps.votes_results:single_option_vote', args=(create_poll.id,))
        }
    
    @pytest.mark.django_db
    def test_config_has_everything(self, test_config):
        self._test_config_has_everything(test_config)
    
    @pytest.mark.django_db
    def test_render_vote_page(self, client, create_poll, test_config):
        """Test rendering of vote page."""
        self._test_render_vote_page(client, create_poll, test_config)
