from django.http import HttpResponse
from django.test import Client
from django.urls import reverse
import pytest
from assertpy import assert_that


class TestLoadVotesPage:
    """Tests to ensure votes pages section load correctly. 
    They include: votes results list of all polls, 
    TODO: add more"""

    @pytest.fixture
    def client(self):
        return Client()
    
    @pytest.mark.django_db
    def test_load_votes_results_page(self, client):
        """Test to ensure votes results page loads without HTTP error"""

        response: HttpResponse = client.get(reverse('apps.votes_results:votable_polls'))
        assert assert_that(response.status_code).is_equal_to(200)