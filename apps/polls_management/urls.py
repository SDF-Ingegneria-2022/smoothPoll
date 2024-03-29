from django.urls import path

from apps.polls_management import views
from allauth.account.decorators import login_required

app_name = 'apps.polls_management'
urlpatterns = [

    # list of all polls
    path('', views.all_user_polls, name='all_user_polls'),

    # create new poll
    path('crea/', views.create_poll_init_view, name="poll_create"),

    # modify or delete a poll
    path('<int:poll_id>/cancella/', views.poll_delete, name='poll_delete'),
    path('<int:poll_id>/modifica/', views.edit_poll_init_view, name="poll_edit"),
    path('<int:poll_id>/apri-scelta/', views.open_poll_by_id, name="poll_open"),
    
    # details page for poll not yet open
    path('<int:poll_id>/dettagli/', login_required(views.poll_details), name='poll_details'),

    # poll token creation and delete page path
    path('<int:poll_id>/generazione-token/', views.poll_token, name='poll_tokens'),
    path('<int:poll_id>/cancellazione-token/', views.delete_poll_token, name='delete_poll_tokens'),

    # page with cards containing qr-code to print
    path('<int:poll_id>/token-pdf/', views.poll_qr_code, name='poll_qr_code'),
    path('<int:poll_id>/pdf_view/<int:page_number>/', views.pdf_view, name="pdf_view"),
    path('<int:poll_id>/pdf_download/<int:page_number>/', views.pdf_download, name="pdf_download"),
    
    #check token 
    path('<int:poll_id>search_view/', views.PollSearchView, name='poll_search'),

    #close poll
    path('<int:poll_id>/close_view/',  login_required(views.ClosePollView.as_view()), name='poll_close'),
        

    # htmx form to create and edit polls
    path('form/', login_required(views.CreatePollHtmxView.as_view()), name="poll_form"),
    path('form/annulla', views.poll_form_clean_go_back_home, name="poll_form_clean_go_back_home"), 
    path('form/htmx/modifica-dati', views.poll_form_htmx_edit, name="poll_form_htmx_edit"), 
    path('form/htmx/aggiungi-opzione', views.poll_form_htmx_create_option, name="poll_form_htmx_create_option"), 
    path('form/htmx/modifica-opzione/<int:option_rel_id>', views.poll_form_htmx_edit_option, name="poll_form_htmx_edit_option"), 
    path('form/htmx/elimina-opzione/<int:option_rel_id>', views.poll_form_htmx_delete_option, name="poll_form_htmx_delete_option"),  

    # page to track create and edit of MJ and SO polls through GA
    path('form/creato-o-modificato-os', views.poll_form_confirm, name="poll_form_confirm_so"),
    path('form/creato-o-modificato-gm', views.poll_form_confirm, name="poll_form_confirm_mj"),    
]
