from django.urls import path

from . import views

app_name = 'polls'
urlpatterns = [

    # simple polls
    path('', views.all_polls, name='all_polls'),
    path('<int:poll_id>/cancellazione/', views.poll_delete, name='poll_delete'),
    path('<int:poll_id>', views.get_poll, name='get_poll'),
    path('<int:poll_id>/conferma-voto/', views.submit_vote, name='submit_vote'),
    path('<int:poll_id>/risultati/', views.results, name='results'),

    # dummy majority judjment poll
    path('dummy/maggioritario/', views.dummy_majority, name='dummy_majority'),
    path('<int:poll_id>/voto-giudizio-maggioritario/', views.dummy_majority, name='majority_vote'),
    path('<int:poll_id>/conferma-voto-maggioritario/', views.majority_vote_submit, name='majority_vote_submit'),
    path('<int:poll_id>/risultati-maggioritario', views.majority_vote_results, name='majority_vote_results'),


    # create poll proces urls
    path('crea-nuovo-deprecated/', views.create_poll_start, name="create-poll"), 
    path('crea-nuovo-deprecated/step1', views.CreatePollStep1View.as_view(), name="create-poll-1"), 
    path('crea-nuovo-deprecated/step2', views.CreatePollStep2View.as_view(), name="create-poll-2"), 
    path('crea-nuovo-deprecated/conferma', views.create_poll_confirm, name="create-poll-confirm"),

    # create poll proces urls
    path('crea-nuovo/', views.create_poll_init_view, name="create_poll_form"), 
    path('<int:poll_id>/modifica', views.edit_poll_init_view, name="edit_poll_form"), 

    path('form-sondaggio/', views.CreatePollHtmxView.as_view(), name="poll_form"), 
    path('form-sondaggio/annulla', views.poll_form_clean_go_back_home, name="poll_form_clean_go_back_home"), 
    path('form-sondaggio/htmx/modifica-dati', views.poll_form_htmx_edit, name="poll_form_htmx_edit"), 
    path('form-sondaggio/htmx/aggiungi-opzione', views.poll_form_htmx_create_option, name="poll_form_htmx_create_option"), 
    path('form-sondaggio/htmx/modifica-opzione/<int:option_rel_id>', views.poll_form_htmx_edit_option, name="poll_form_htmx_edit_option"), 
    path('form-sondaggio/htmx/elimina-opzione/<int:option_rel_id>', views.poll_form_htmx_delete_option, name="poll_form_htmx_delete_option"), 
]
