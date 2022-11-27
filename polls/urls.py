from django.urls import path

from . import views

app_name = 'polls'
urlpatterns = [
    path('', views.all_polls, name='all_polls'),
    path('dummy/', views.dummy, name='dummy'),
    path('dummy/submit-vote/', views.submit_vote, name='submit_vote'),
    path('dummy/results/', views.results, name='results'),
]