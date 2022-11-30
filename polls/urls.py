from django.urls import path

from . import views

app_name = 'polls'
urlpatterns = [
    path('', views.all_polls, name='all_polls'),
    path('dummy/', views.dummy, name='dummy'),
    path('dummy/conferma-voto/', views.submit_vote, name='submit_vote'),
    path('dummy/risultati/', views.results, name='results'),
    path('dummy/maggioritario/', views.dummy_majority, name='dummy-majority'),
    path('dummt/risultati-maggioritario', views.majority_results, name='majority-results'),

    # create poll proces urls
    path('crea-nuovo/', views.create_poll_start, name="create-poll"), 
    path('crea-nuovo/step1', views.CreatePollStep1View.as_view(), name="create-poll-1"), 
    path('crea-nuovo/step2', views.create_poll_step_2_view, name="create-poll-2"), 
]