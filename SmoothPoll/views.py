from django.shortcuts import render


def home(request):
    """
    App home page
    """

    return render(request, "global/home.html")