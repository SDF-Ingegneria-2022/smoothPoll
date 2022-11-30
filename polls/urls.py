from django.urls import path

from . import views

app_name = 'polls'
urlpatterns = [
    path('', views.all_polls, name='all_polls'),
    path('<int:poll_id>', views.get_poll, name='get_poll'),
    path('<int:poll_id>/conferma-voto/', views.submit_vote, name='submit_vote'),
    
    path('dummy/risultati/', views.results, name='results'),
    path('dummy/maggioritario/', views.dummy_majority, name='dummy-majority'),
    path('dummt/risultati-maggioritario', views.majority_results, name='majority-results'),

    # create poll proces urls
    path('crea-nuovo/', views.create_poll_start, name="create-poll"), 
    path('crea-nuovo/step1', views.CreatePollStep1View.as_view(), name="create-poll-1"), 
    path('crea-nuovo/step2', views.CreatePollStep2View.as_view(), name="create-poll-2"), 
    path('crea-nuovo/conferma', views.create_poll_confirm, name="create-poll-confirm")
]