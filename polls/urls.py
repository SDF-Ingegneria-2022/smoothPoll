from django.urls import path

from . import views

app_name = 'polls'
urlpatterns = [
    path('', views.index, name='index'),
    path('dummy/', views.dummy, name='dummy'),
    path('dummy/submit-vote/', views.submit_vote, name='submit_vote'),
    path('dummy/results/', views.results, name='results'),
    path('dummy/vote-error/', views.vote_error, name='vote_error'),
    path('dummy-majority/', views.dummy_majority, name='dummy-majority'),
    path('dummy-majority/results', views.majority_results, name='majority-results'),
]