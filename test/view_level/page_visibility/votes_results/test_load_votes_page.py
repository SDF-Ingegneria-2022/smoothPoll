from django.http import HttpResponse
from django.test import Client
from django.urls import reverse
import pytest
from assertpy import assert_that

from test.view_level.utils.test_with_client import TestWithClient


class TestLoadVotesPage(TestWithClient):
    """Tests to ensure votes page section load correctly. """
    
    @pytest.mark.django_db
    def test_load_votes_results_page(self, client: Client):
        """Test to ensure votes results page loads without HTTP error"""

        response: HttpResponse = client.get(reverse('apps.votes_results:votable_polls'))
        assert_that(response.status_code).is_equal_to(200)