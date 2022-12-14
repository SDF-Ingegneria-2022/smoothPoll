"""SmoothPoll URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [

    # home page
    path('', views.home, name="home"),
    
    # area to manage your polls (open, close, CRUD operations)
    path('gestione-sondaggi/', include('apps.polls_management.urls'), name="polls_management"),

    # area to vote and view results
    path('voti-e-risultati/', include('apps.votes_results.urls'), name="votes_results"),

    # admin auth
    path('admin/', admin.site.urls),
]

handler404 = 'SmoothPoll.views.error_404_view'