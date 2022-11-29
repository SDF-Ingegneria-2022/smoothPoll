from django.urls import path

from . import views

app_name = 'polls'
urlpatterns = [
    path('<int:page>', views.all_polls, name='all_polls'),
    path('dummy/', views.dummy, name='dummy'),
    path('dummy/conferma-voto/', views.submit_vote, name='submit_vote'),
    path('dummy/risultati/', views.results, name='results'),
    path('dummy/maggioritario/', views.dummy_majority, name='dummy-majority'),
    path('dummt/risultati-maggioritario', views.majority_results, name='majority-results'),
    path('crea-nuovo/', views.create_poll_view, name="create-poll")
]