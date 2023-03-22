from django.http import HttpRequest, HttpResponse
from django.test import Client
from django.urls import reverse
import pytest
from assertpy import assert_that
from apps.polls_management.classes.poll_form_utils.poll_form_session import SESSION_ERROR, SESSION_FORMDATA, SESSION_IS_EDIT, SESSION_OPTIONS, SESSION_POLL_ID

from test.view_level.utils.test_with_client import TestWithClient


class TestFormSessionInit(TestWithClient):
    """Tests to ensure form session is init correctly by create and edit processes"""

    @pytest.mark.django_db
    def test_create_init_session(self, auth_client: Client):
        """Ensure after create request session is clean"""

        # Start create process (as auth)
        response: HttpResponse = auth_client.get(reverse('apps.polls_management:poll_create'))
        
        # Check session is init correctly (I expect clear env.)
        assert_that(auth_client.session.get(SESSION_FORMDATA)).is_none()
        assert_that(auth_client.session.get(SESSION_POLL_ID)).is_none()
        assert_that(auth_client.session.get(SESSION_OPTIONS)).is_none()
        assert_that(auth_client.session.get(SESSION_ERROR)).is_none()
        assert_that(auth_client.session.get(SESSION_IS_EDIT)).is_none()


