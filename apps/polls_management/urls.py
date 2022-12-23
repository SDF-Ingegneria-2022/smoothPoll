from django.urls import path

from apps.polls_management import views

app_name = 'apps.polls_management'
urlpatterns = [

    # list of all polls
    path('', views.all_polls, name='all_polls'),

    # create new poll
    path('crea/', views.create_poll_init_view, name="poll_create"),

    # modify or delete a poll
    path('<int:poll_id>/cancella/', views.poll_delete, name='poll_delete'),
    path('<int:poll_id>/modifica/', views.edit_poll_init_view, name="poll_edit"), 

    # htmx form for create and edit polls
    path('form/', views.CreatePollHtmxView.as_view(), name="poll_form"), 
    path('form/annulla', views.poll_form_clean_go_back_home, name="poll_form_clean_go_back_home"), 
    path('form/htmx/modifica-dati', views.poll_form_htmx_edit, name="poll_form_htmx_edit"), 
    path('form/htmx/aggiungi-opzione', views.poll_form_htmx_create_option, name="poll_form_htmx_create_option"), 
    path('form/htmx/modifica-opzione/<int:option_rel_id>', views.poll_form_htmx_edit_option, name="poll_form_htmx_edit_option"), 
    path('form/htmx/elimina-opzione/<int:option_rel_id>', views.poll_form_htmx_delete_option, name="poll_form_htmx_delete_option"), 

    # create poll proces urls (TODO: delete, it is deprecated)
    path('crea-nuovo-deprecated/', views.create_poll_start, name="create-poll"), 
    path('crea-nuovo-deprecated/step1', views.CreatePollStep1View.as_view(), name="create-poll-1"), 
    path('crea-nuovo-deprecated/step2', views.CreatePollStep2View.as_view(), name="create-poll-2"), 
    path('crea-nuovo-deprecated/conferma', views.create_poll_confirm, name="create-poll-confirm"),
]
