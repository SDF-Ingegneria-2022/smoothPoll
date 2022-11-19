from django.urls import path

from . import views

app_name = 'polls'
urlpatterns = [
    path('', views.index, name='index'),
    path('dummy/', views.dummy, name='dummy'),
    path('submit-vote/', views.submit_vote, name='submit_vote'),
    path('results/', views.results, name='results'),
    path('vote-error/', views.vote_error, name='vote_error'),
]