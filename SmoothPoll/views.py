from django.shortcuts import render
from apps.polls_management.models.poll_model import PollModel

def home(request):
    """
    App home page
    """
    predefined_polls = PollModel.objects.filter(predefined=True)
    return render(request, "global/home.html",
                  {"predefined_polls": predefined_polls})

def error_404_view(request, exception):
    """
    Page 404 handler view. It is called when a page is not found.
    """
    return render(request, 'global/404.html')