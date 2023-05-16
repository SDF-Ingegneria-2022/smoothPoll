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
    path('<int:poll_id>/scegli-o-giudica/', views.generic_vote_view, name='vote'), 
    path('<int:poll_id>/risultati/', views.generic_results_view, name='results'), 

    # vote-recap-results process for single option
    path('<int:poll_id>/scelta-singola/', views.SingleOptionVoteView.as_view(), name='single_option_vote'),
    path('<int:poll_id>/riepilogo-scelta-singola/', views.single_option_recap_view, name='single_option_recap'),
    path('<int:poll_id>/risultati/scelta-singola/', views.single_option_results_view, name='single_option_results'),

    # vote-recap-results process for majority judgment
    path('<int:poll_id>/giudizio-maggioritario/', views.MajorityJudgmentVoteView.as_view(), name='majority_judgment_vote'),
    path('<int:poll_id>/riepilogo-giudizio-maggioritario/', views.majority_judgment_recap_view, name='majority_judgment_recap'),
    path('<int:poll_id>/risultati/giudizio-maggioritario/', views.majority_judgment_results_view, name='majority_judgment_results'),

    # dummy majority judjment poll
    path('prova-giudizio-maggioritario/', views.MajorityJudgmentVoteView.as_view(), name='dummy_majority'),

    # vote process for schulze method
    path('<int:poll_id>/metodo-schulze/', views.SchulzeMethodVoteView.as_view(), name='schulze_method_vote'),
    path('<int:poll_id>/riepilogo-metodo-schulze/', views.schulze_method_recap_view, name='schulze_method_recap'),

    # expose endpoint to sort option after a post request
    path('<int:poll_id>/metodo-schulze/sort/', views.sort, name='sort'),

    # old urls (kept w redirect for retro-compatibility)
    # path('<int:poll_id>/vota/', views.redirect_to_vote, name='vote_redirect_legacy'), 
    # path('<int:poll_id>/vota/scelta-singola/', views.SingleOptionVoteView.as_view(), name='single_option_vote'),
    # path('<int:poll_id>/riepilogo-scelta/scelta-singola/', views.single_option_recap_view, name='single_option_recap'),
    # path('<int:poll_id>/vota/giudizio-maggioritario/', views.MajorityJudgmentVoteView.as_view(), name='majority_judgment_vote'),
    # path('<int:poll_id>/riepilogo-scelta/giudizio-maggioritario/', views.majority_judgment_recap_view, name='majority_judgment_recap')
]