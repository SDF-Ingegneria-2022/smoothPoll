from django.http import HttpResponse
from django.test import Client
from django.urls import reverse
import pytest
from assertpy import assert_that


class TestLoadSecondaryPages:
    """Tests to ensure all secondary pages load correctly. 
    They include: attributions, admin page, social login page, etc. """

    @pytest.fixture
    def client(self):
        return Client()

    @pytest.mark.django_db
    def test_load_attribution_page(self, client):
        """Test to ensure attribution page loads without HTTP error"""

        response: HttpResponse = client.get(reverse('attributions'))
        assert assert_that(response.status_code).is_equal_to(200)

    @pytest.mark.django_db
    def test_load_admin_page(self, client):
        """Test to ensure admin page loads without HTTP error"""

        response: HttpResponse = client.get('admin/')
        assert assert_that(response.status_code).is_equal_to(200)

    @pytest.mark.django_db
    def test_load_google_login_page(self, client):
        """Test to ensure google login page loads without HTTP error"""

        response: HttpResponse = client.get('accounts/google/login-page/')
        assert assert_that(response.status_code).is_equal_to(200)