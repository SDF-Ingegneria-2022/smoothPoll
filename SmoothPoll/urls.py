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
    # detail poll page
    path('<str:poll_short_id>', views.poll_details_page, name="poll_details_page"),
    # attributions for creative commons licence
    path('attribuzioni-creative-commons/', views.attributions, name="attributions"),

    # info pages
    path('info/', views.general_info, name="general_info"),
    path('info/opzione-singola', views.single_option_info, name="single_option_info"),
    path('info/giudizio-maggioritario', views.majority_judgment_info, name="majority_judgment_info"),
    path('info/metodo-schulze', views.schulze_method_info, name="schulze_method_info"),
    
    # area to manage your polls (open, close, CRUD operations)
    path('gestione-scelte/', include('apps.polls_management.urls'), name="polls_management"),

    # area to vote and view results
    # path('voti-e-risultati/', include('apps.votes_results.urls'), name="votes_results"),
    path('scelte-e-risultati/', include('apps.votes_results.urls'), name="votes_results"),

    # admin auth
    path('admin/', admin.site.urls),

    # redirect page to login
    path('accounts/google/login-page/', views.login_redirect_page),

    # login urls disabled
    path('accounts/signup/', views.error_404_view_redirect),
    path('accounts/login/', views.error_404_view_redirect),
    path('accounts/password/change/', views.error_404_view_redirect),
    path('accounts/password/set/', views.error_404_view_redirect),
    path('accounts/inactive/', views.error_404_view_redirect),
    path('accounts/email/', views.error_404_view_redirect),
    path('accounts/confirm-email/', views.error_404_view_redirect),
    path('accounts/password/reset/done/', views.error_404_view_redirect),
    path('accounts/social/', views.error_404_view_redirect),
    path('accounts/social/signup/', views.error_404_view_redirect),
    path('accounts/social/connections/', views.error_404_view_redirect),

    # google auth url 
    path('accounts/', include('allauth.urls')),
    # path('/', include('google_login.urls')),

]

handler404 = 'SmoothPoll.views.error_404_view'
