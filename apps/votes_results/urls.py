from django.urls import path

from apps.votes_results import views

app_name = 'apps.votes_results'
urlpatterns = [

    # vote-recap-results process for single option
    path('<int:poll_id>/vota/scelta-singola/', views.single_option_vote, name='single_option_vote'),
    path('<int:poll_id>/riepilogo-voto/scelta-singola/', views.single_option_recap, name='single_option_recap'),
    path('<int:poll_id>/risultati/scelta-singola/', views.single_option_results, name='single_option_results'),

    # vote-recap-results process for majority judgment
    path('<int:poll_id>/vota/giudizio-maggioritario/', views.majority_judgment_vote, name='majority_judgment_vote'),
    path('<int:poll_id>/riepilogo-voto/giudizio-maggioritario/', views.majority_judgment_recap, name='majority_judgment_recap'),
    path('<int:poll_id>/risultati/giudizio-maggioritario/', views.majority_judgment_results, name='majority_judgment_results'),

    # dummy majority judjment poll
    path('prova-voto-maggioritario/', views.majority_judgment_vote, name='dummy_majority'),
]