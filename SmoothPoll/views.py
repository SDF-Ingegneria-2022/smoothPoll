from django.http import Http404
from django.shortcuts import render
from django.urls import reverse
from apps.polls_management.models.poll_model import PollModel
import configparser

from apps.polls_management.views.poll_short_id_view import PollShortIdView

def home(request):
    """
    App home page
    """
    predefined_polls = PollModel.objects.filter(predefined=True)

    return render(request, "global/home.html",
                  {"predefined_polls": predefined_polls, })

def attributions(request):
    """Attributions for Creative Common material"""
    return render(request, "global/attributions.html")

def login_redirect_page(request):
    """Page to redirect to login when the user tries to do
    authentication-only procedures"""

    return render(request, 'global/login.html')

def error_404_view(request, exception):
    """
    Page 404 handler view. It is called when a page is not found.
    """
    return render(request, 'global/404.html')

def error_404_view_redirect(request):
    """
    Page 404 handler view redirect. It is called when a page is not found.
    """
    raise Http404()

def poll_details_page(request, poll_short_id):
    """
    Page to show the details of a poll.
    """
    return PollShortIdView.as_view()(request, poll_short_id)
    