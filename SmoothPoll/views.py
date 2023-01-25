from django.http import Http404
from django.shortcuts import render
from apps.polls_management.models.poll_model import PollModel
import configparser

def home(request):
    """
    App home page
    """
    predefined_polls = PollModel.objects.filter(predefined=True)
    config = configparser.ConfigParser()
    config.read('.bumpversion.cfg')
    version = config.get('bumpversion', 'current_version')
    return render(request, "global/home.html",
                  {"predefined_polls": predefined_polls, 
                   "version": version})

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