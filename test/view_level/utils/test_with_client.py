

from django.test import Client
import pytest


class TestWithClient:
    """Base class for a test which uses a (auth or not) client"""

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


