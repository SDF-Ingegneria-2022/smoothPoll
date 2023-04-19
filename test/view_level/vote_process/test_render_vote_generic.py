
import abc
import pytest
from test.service_level.utils.create_polls_utils import create_single_option_polls
from test.view_level.utils.test_with_client import TestWithClient
from assertpy import assert_that


class TestRenderVoteGeneric(TestWithClient, abc.ABC):

    @pytest.fixture
    def create_poll(self, django_user_model):
        return create_single_option_polls(django_user_model, number_of_polls=1)[0]

    def _test_render_vote_page(self, create_poll, test_config):
        """Test rendering of vote page."""
        assert_that(test_config).contains_key("prova")
        
        

