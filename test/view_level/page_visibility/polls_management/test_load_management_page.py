from django.http import HttpResponse
from django.test import Client
from django.urls import reverse
import pytest
from assertpy import assert_that

from test.view_level.utils.test_with_client import TestWithClient


class TestLoadManagementPage(TestWithClient):
    """Tests to ensure management page section load correctly. """
    
    @pytest.mark.django_db
    def test_management_requires_auth(self, client: Client):
        """Test to ensure management page redirect to login 
        (because it requires authentication)"""

        response: HttpResponse = client.get(reverse('apps.polls_management:all_user_polls'))
        assert_that(response.status_code).is_equal_to(302)
        assert_that(response.url).is_equal_to(
            '/accounts/google/login-page/?next=' + \
            reverse('apps.polls_management:all_user_polls'))

    @pytest.mark.django_db
    def test_management_loads_as_auth(self, auth_client: Client):
        """Test to ensure management page loads without HTTP error"""

        response: HttpResponse = auth_client.get(reverse('apps.polls_management:all_user_polls'))
        assert_that(response.status_code).is_equal_to(200)
