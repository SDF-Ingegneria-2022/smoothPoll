import pytest
from test.view_level.vote_process.test_render_vote_generic import TestRenderVoteGeneric


class TestRenderVoteSO(TestRenderVoteGeneric):

    @pytest.fixture
    def test_config(self):
        return {"prova": "ciao"}
    
    @pytest.mark.django_db
    def test_render_vote_page(self, create_poll, test_config):
        """Test rendering of vote page."""
        self._test_render_vote_page(create_poll, test_config)
