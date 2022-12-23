from django.urls import path

from apps.polls_management import views

app_name = 'apps.votes_results'
urlpatterns = [
    path('<int:poll_id>/', views.get_poll, name='single_option_vote'),
    path('<int:poll_id>/conferma-voto/', views.submit_vote, name='single_option_recap'),
    path('<int:poll_id>/risultati/', views.results, name='single_option_results'),

    # dummy majority judjment poll
    path('dummy/maggioritario/', views.dummy_majority, name='dummy_majority'),
    path('<int:poll_id>/voto-giudizio-maggioritario/', views.dummy_majority, name='majority_judgment_vote'),
    path('<int:poll_id>/conferma-voto-maggioritario/', views.majority_vote_submit, name='majority_judgment_recap'),
    path('<int:poll_id>/risultati-maggioritario', views.majority_vote_results, name='majority_judgment_results'),
]