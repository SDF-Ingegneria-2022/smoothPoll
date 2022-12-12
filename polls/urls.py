from django.urls import path

from . import views

app_name = 'polls'
urlpatterns = [

    # simple polls
    path('', views.all_polls, name='all_polls'),
    path('<int:poll_id>', views.get_poll, name='get_poll'),
    path('<int:poll_id>/conferma-voto/', views.submit_vote, name='submit_vote'),
    path('<int:poll_id>/risultati/', views.results, name='results'),

    # dummy majority judjment poll
    path('dummy/maggioritario/', views.dummy_majority, name='dummy_majority'),
    path('<int:poll_id>/conferma-voto-maggioritario/', views.majority_vote_submit, name='majority_vote_submit'),
    path('<int:poll_id>/risultati-maggioritario', views.majority_vote_results, name='majority_vote_results'),


    # create poll proces urls
    path('crea-nuovo/', views.create_poll_start, name="create-poll"), 
    path('crea-nuovo/step1', views.CreatePollStep1View.as_view(), name="create-poll-1"), 
    path('crea-nuovo/step2', views.CreatePollStep2View.as_view(), name="create-poll-2"), 
    path('crea-nuovo/conferma', views.create_poll_confirm, name="create-poll-confirm"),

    # experiment htmx
    path('prova-htmx/<int:poll_id>/', views.htmx_example_page, name='htmx-create-poll'), 
    path('prova-htmx/<int:poll_id>/cancella-opzione/<int:option_id>', views.htmx_delete_option, name='htmx-delete-option'), 

]
