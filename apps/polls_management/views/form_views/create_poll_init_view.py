
from apps.polls_management.classes.poll_form_utils.poll_form_session import clean_session
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse
from allauth.account.decorators import login_required


@login_required
def create_poll_init_view(request: HttpRequest):
    """View to inizialize form for new poll creation"""

    # clean session from eventual mess
    clean_session(request)

    # poll and option will be inited creating new ones
    # (because session is clean)
    
    # redirect to form to permit edit
    return HttpResponseRedirect(reverse('apps.polls_management:poll_form'))       