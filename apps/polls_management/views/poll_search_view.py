from django.http import Http404, HttpResponseRedirect, HttpRequest
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from apps.polls_management.models.poll_model import PollModel


def PollSearchView(request:HttpRequest, poll_id):
    """ View used to access poll by giving a valid token as input in token redirect page."""

    token_string: str = request.GET.get('token')

    try:
        poll: PollModel = PollModel.objects.get(id=poll_id)
    except ObjectDoesNotExist:
        raise Http404()

    poll_shortid: str = poll.short_id

    return HttpResponseRedirect(
                        reverse('poll_details_page', args=(poll_shortid,)) + '?token=' + token_string)
