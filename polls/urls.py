from django.urls import path

from . import views

app_name = 'polls'
urlpatterns = [
    path('', views.all_polls, name='all_polls'),
    path('dummy/', views.dummy, name='dummy'),
    path('dummy/conferma-voto/', views.submit_vote, name='submit_vote'),
    path('dummy/risultati/', views.results, name='results'),
]