
import abc
from datetime import timedelta
from django.http import HttpResponse
import pytest
from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.models.poll_token import PollTokens
from apps.polls_management.services.poll_token_service import PollTokenService
from test.service_level.utils.create_polls_utils import create_single_option_polls
from test.view_level.utils.test_with_client import TestWithClient
from assertpy import assert_that
from django.utils import timezone


class TestRenderVoteGeneric(TestWithClient, abc.ABC):

    def _make_poll_open(self, create_poll):
        create_poll.open_datetime = timezone.now()
        create_poll.close_datetime = timezone.now() + timedelta(days=1)
        create_poll.save()

    def _make_poll_not_yet_open(self, create_poll):
        create_poll.open_datetime = timezone.now() + timedelta(days=1)
        create_poll.close_datetime = timezone.now() + timedelta(days=2)
        create_poll.save() 

    def _make_poll_closed(self, create_poll):
        create_poll.open_datetime = timezone.now() - timedelta(days=2)
        create_poll.close_datetime = timezone.now() - timedelta(days=1)
        create_poll.save() 

    def _make_poll_token_votable(self, create_poll) -> PollTokens:
        create_poll.protection = PollModel.PollVoteProtection.TOKEN
        create_poll.save()

        return PollTokenService.create_tokens(1, create_poll)[0]
    
    def _vote_with_token(self, poll, token):
        if poll.poll_type == PollModel.PollType.SINGLE_OPTION:
            PollTokenService.check_single_option(token)
        else:
            PollTokenService.check_majority_option(token)

    
    def _test_config_has_everything(self, test_config):
        """Meta-test to ensure that the test config has everything it needs."""
        
        # ensure all urls are specified
        assert_that(test_config).contains_key("vote_page_url")
        assert_that(test_config).contains_key("short_id_url")
        assert_that(test_config).contains_key("generic_vote_url")

        # ensure all expected templates are specified
        assert_that(test_config).contains_key("vote_page_template")
        assert_that(test_config).contains_key("poll_not_yet_open_template")
        assert_that(test_config).contains_key("poll_closed_template")
        assert_that(test_config).contains_key("insert_token_template")

    def _test_render_vote_page(self, client, create_poll, test_config):
        """Test to ensure that an open poll renders the vote page"""
        
        self._make_poll_open(create_poll)

        response: HttpResponse = client.get(test_config["vote_page_url"])

        assert_that(response.status_code).is_equal_to(200)
        assert_that(response.templates[0].name).is_equal_to(test_config["vote_page_template"])

    def _test_not_yet_open_poll_page(self, client, create_poll, test_config):
        """Test to ensure that a not-yet-open displays a "wait" page"""

        self._make_poll_not_yet_open(create_poll)

        response = client.get(test_config["vote_page_url"])

        assert_that(response.status_code).is_equal_to(200)
        assert_that(response.templates[0].name).is_not_equal_to(test_config["vote_page_template"])
        assert_that(response.templates[0].name).is_equal_to(test_config["poll_not_yet_open_template"])

    def _test_already_closed_poll_page(self, client, create_poll, test_config): 
        """Test to ensure that a closed poll displays a "closed" page"""

        self._make_poll_closed(create_poll)

        response = client.get(test_config["vote_page_url"])

        assert_that(response.status_code).is_equal_to(200)
        assert_that(response.templates[0].name).is_not_equal_to(test_config["vote_page_template"])
        assert_that(response.templates[0].name).is_equal_to(test_config["poll_closed_template"])

    def _test_generic_vote_redirect(self, client, create_poll, test_config):
        """Test to ensure that generic vote are redirected to the proper vote page"""

        self._make_poll_open(create_poll)

        response = client.get(test_config["generic_vote_url"])

        assert_that(response.status_code).is_equal_to(302)
        assert_that(response.url).is_equal_to(test_config["vote_page_url"])

    def _test_short_id_redirect(self, client, create_poll, test_config):
        """Test to ensure that short IDs are redirected to generic vote url"""

        self._make_poll_open(create_poll)

        response = client.get(test_config["short_id_url"])

        assert_that(response.status_code).is_equal_to(302)
        assert_that(response.url).is_equal_to(test_config["generic_vote_url"])

        response2 = client.get(response.url)

        assert_that(response2.status_code).is_equal_to(302)
        assert_that(response2.url).is_equal_to(test_config["vote_page_url"])

    def _test_render_vote_page_w_token(self, client, create_poll, test_config):
        """Test to ensure that a token protected choice can be accessed calling the token link"""

        self._make_poll_open(create_poll)
        token = self._make_poll_token_votable(create_poll)

        # call short id passing token as param
        response = client.get(test_config["short_id_url"]  + token.get_token_query_string())

        # expect redirect to vote view 
        # TODO: solve incoerence w vote without token!
        assert_that(response.status_code).is_equal_to(302)
        assert_that(response.url).is_equal_to(test_config["vote_page_url"])

        # call redirect url and expect I can vote
        response2 = client.get(response.url)
        assert_that(response2.status_code).is_equal_to(200)
        assert_that(response2.templates[0].name).is_equal_to(test_config["vote_page_template"])

    def _test_missing_token(self, client, create_poll, test_config):
        """Test to ensure that a token protected choice cannot be accessed without a token"""

        self._make_poll_open(create_poll)
        self._make_poll_token_votable(create_poll)

        # call short id without passing token as param
        # (expect not the vote page)
        response = client.get(test_config["short_id_url"])
        assert_that(response.templates[0].name).is_not_equal_to(test_config["vote_page_template"])
        assert_that(response.templates[0].name).is_equal_to(test_config["insert_token_template"])

        # call generic link without passing token as param
        # (expect not the vote page)
        response = client.get(test_config["generic_vote_url"])
        assert_that(response.templates[0].name).is_not_equal_to(test_config["vote_page_template"])
        assert_that(response.templates[0].name).is_equal_to(test_config["insert_token_template"])

        # call specific vote page without passing token as param
        # (expect not the vote page)
        response = client.get(test_config["vote_page_url"])
        assert_that(response.templates[0].name).is_not_equal_to(test_config["vote_page_template"])
        assert_that(response.templates[0].name).is_equal_to(test_config["insert_token_template"])

    def _test_wrong_token(self, client, create_poll, test_config):
        """Test to ensure that a token protected choice cannot be accessed with a wrong token"""

        self._make_poll_open(create_poll)
        self._make_poll_token_votable(create_poll)

        # call short id passing wrong token as param
        # (expect not the vote page)
        response = client.get(test_config["short_id_url"] + "?token=wrongtoken")
        assert_that(response.templates[0].name).is_not_equal_to(test_config["vote_page_template"])
        assert_that(response.templates[0].name).is_equal_to(test_config["insert_token_template"])

        # call generic link passing wrong token as param
        # (expect not the vote page)
        response = client.get(test_config["generic_vote_url"] + "?token=wrongtoken")
        assert_that(response.templates[0].name).is_not_equal_to(test_config["vote_page_template"])
        assert_that(response.templates[0].name).is_equal_to(test_config["insert_token_template"])

        # call specific vote page passing wrong token as param
        # (expect not the vote page)
        response = client.get(test_config["vote_page_url"] + "?token=wrongtoken")
        assert_that(response.templates[0].name).is_not_equal_to(test_config["vote_page_template"])
        assert_that(response.templates[0].name).is_equal_to(test_config["insert_token_template"])

    def _test_used_token(self, client, create_poll, test_config):
        """Test to ensure that a token protected choice cannot be accessed with an already used token"""

        self._make_poll_open(create_poll)
        token = self._make_poll_token_votable(create_poll)
        self._vote_with_token(create_poll, token)

        # call short id passing used token as param
        # (expect not the vote page)
        response = client.get(test_config["short_id_url"] + token.get_token_query_string())
        assert_that(response.templates[0].name).is_not_equal_to(test_config["vote_page_template"])
        assert_that(response.templates[0].name).is_equal_to(test_config["insert_token_template"])

        # call generic link passing used token as param
        # (expect not the vote page)
        response = client.get(test_config["generic_vote_url"] + token.get_token_query_string())
        assert_that(response.templates[0].name).is_not_equal_to(test_config["vote_page_template"])
        assert_that(response.templates[0].name).is_equal_to(test_config["insert_token_template"])

        # call specific vote page passing used token as param
        # (expect not the vote page)
        response = client.get(test_config["vote_page_url"] + token.get_token_query_string())
        assert_that(response.templates[0].name).is_not_equal_to(test_config["vote_page_template"])
        assert_that(response.templates[0].name).is_equal_to(test_config["insert_token_template"])



        
        

