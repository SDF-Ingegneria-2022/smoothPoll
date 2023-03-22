from django.http import HttpResponse
from django.test import Client
from django.urls import reverse
import pytest
from assertpy import assert_that

from test.view_level.utils.test_with_client import TestWithClient


class TestLoadFormPage(TestWithClient):
    """Tests to ensure form page and all related urls load correctly. """
    
    @pytest.mark.django_db
    def test_create_requires_auth(self, client: Client):
        """Test to ensure create page redirect to Google login 
        (because it requires authentication)"""

        response: HttpResponse = client.get(reverse('apps.polls_management:poll_create'))
        
        assert_that(response.status_code).is_equal_to(302)
        assert_that(response.url).is_equal_to(
            '/accounts/google/login-page/?next=' + \
            reverse('apps.polls_management:poll_create'))
        
    @pytest.mark.django_db
    def test_form_requires_auth(self, client: Client):
        """Test to ensure form page redirect to Google login"""
            
        response: HttpResponse = client.get(reverse('apps.polls_management:poll_form'))
        
        assert_that(response.status_code).is_equal_to(302)
        assert_that(response.url).is_equal_to(
            '/accounts/google/login-page/?next=' + \
            reverse('apps.polls_management:poll_form'))
        
    @pytest.mark.django_db
    def test_form_loads_after_create_as_auth(self, auth_client: Client):
        """Test create process leads to a (working) form page"""

        # Start create process (as auth)
        response: HttpResponse = auth_client.get(reverse('apps.polls_management:poll_create'))
        
        # ensure response is expected redirect
        assert_that(response.status_code).is_equal_to(302)
        assert_that(response.url).is_equal_to(reverse('apps.polls_management:poll_form'))

        # Perform asked redirect and ensure form page loaded correctly 
        response: HttpResponse = auth_client.get(response.url)
        assert_that(response.status_code).is_equal_to(200)

