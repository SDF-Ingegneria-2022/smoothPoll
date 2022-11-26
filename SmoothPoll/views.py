from django.shortcuts import render


def home(request):
    """
    App home page
    """

    return render(request, "global/home.html")

def error_404_view(request, exception):
    """
    Page 404 handler view. It is called when a page is not found.
    """
    return render(request, 'global/404.html')