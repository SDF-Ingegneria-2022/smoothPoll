from django.http import HttpResponse
from django.test import Client
from django.urls import reverse
import pytest
from assertpy import assert_that

from test.view_level.utils.test_with_client import TestWithClient


class TestLoadHomePage(TestWithClient):
    """Test to ensure home page loads correctly"""

    @pytest.mark.django_db
    def test_load_home_page(self, client: Client):
        """Test to ensure home page loads without HTTP error"""

        response: HttpResponse = client.get(reverse('home'))
        assert_that(response.status_code).is_equal_to(200)
