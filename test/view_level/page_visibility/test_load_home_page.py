from django.http import HttpResponse
from django.test import Client
from django.urls import reverse
import pytest
from assertpy import assert_that


class TestLoadHomePage:
    """Test to ensure home page loads correctly"""

    @pytest.fixture
    def client(self):
        return Client()

    @pytest.mark.django_db
    def test_load_home_page(self, client):
        """Test to ensure home page loads without HTTP error"""

        response: HttpResponse = client.get(reverse('home'))
        assert assert_that(response.status_code).is_equal_to(200)
