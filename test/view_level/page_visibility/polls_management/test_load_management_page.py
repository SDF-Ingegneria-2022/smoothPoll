from django.http import HttpResponse
from django.test import Client
from django.urls import reverse
import pytest
from assertpy import assert_that


class TestLoadManagementPage:
    """Tests to ensure management page section load correctly. """

    @pytest.fixture
    def client(self):
        """Not auth client"""
        return Client()
    
    @pytest.fixture
    def auth_client(self, client, django_user_model):
        """Client with authentication"""

        user = django_user_model.objects.create_user(username='test', password='test')
        client.force_login(user)
        return client
    
    @pytest.mark.django_db
    def test_management_requires_auth(self, client):
        """Test to ensure management page redirect to login 
        (because it requires authentication)"""

        response: HttpResponse = client.get(reverse('apps.polls_management:all_user_polls'))
        assert assert_that(response.status_code).is_equal_to(302)

    @pytest.mark.django_db
    def test_management_loads_as_auth(self, auth_client):
        """Test to ensure management page loads without HTTP error"""

        response: HttpResponse = auth_client.get(reverse('apps.polls_management:all_user_polls'))
        assert assert_that(response.status_code).is_equal_to(200)
