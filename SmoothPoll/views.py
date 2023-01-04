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

def error_404_view(request, exception):
    """
    Page 404 handler view. It is called when a page is not found.
    """
    return render(request, 'global/404.html')