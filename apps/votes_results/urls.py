from django.urls import path

from apps.votes_results import views
from allauth.account.decorators import login_required

app_name = 'apps.votes_results'
urlpatterns = [
    #list of all votable polls
    path('', views.all_votable_polls, name='votable_polls'),

    # details page for poll not yet open
    #path('<int:poll_id>/dettagli/', login_required(views.SingleOptionVoteView.as_view()), name='poll_details'),

    # generic vote and results (it will be redirect to main method)
    path('<int:poll_id>/vota/', views.generic_vote_view, name='vote'), 
    path('<int:poll_id>/risultati/', views.generic_results_view, name='results'), 

    # vote-recap-results process for single option
    path('<int:poll_id>/vota/scelta-singola/', views.SingleOptionVoteView.as_view(), name='single_option_vote'),
    path('<int:poll_id>/riepilogo-voto/scelta-singola/', views.single_option_recap_view, name='single_option_recap'),
    path('<int:poll_id>/risultati/scelta-singola/', views.single_option_results_view, name='single_option_results'),

    # vote-recap-results process for majority judgment
    path('<int:poll_id>/vota/giudizio-maggioritario/', views.MajorityJudgmentVoteView.as_view(), name='majority_judgment_vote'),
    path('<int:poll_id>/riepilogo-voto/giudizio-maggioritario/', views.majority_judgment_recap_view, name='majority_judgment_recap'),
    path('<int:poll_id>/risultati/giudizio-maggioritario/', views.majority_judgment_results_view, name='majority_judgment_results'),

    # dummy majority judjment poll
    path('prova-voto-maggioritario/', views.MajorityJudgmentVoteView.as_view(), name='dummy_majority'),
]