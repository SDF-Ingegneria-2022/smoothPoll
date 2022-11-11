from django.urls import path

from . import views

app_name = 'polls'
urlpatterns = [
    path('', views.index, name='index'),
    path('dummy/', views.dummy, name='dummy'),
    path('submit-vote/', views.submit_vote, name='submit_vote'),
]