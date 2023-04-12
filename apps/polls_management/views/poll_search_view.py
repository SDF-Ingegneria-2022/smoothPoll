from django.http import Http404, HttpResponseRedirect, HttpRequest
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.core.exceptions import ObjectDoesNotExist
from apps.polls_management.constants.template_path_constants import POLL_DETAILS_PAGE_TEMPLATE_PATH
from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.models.poll_token import PollTokens
from apps.polls_management.services.poll_token_service import PollTokenService
from apps.votes_results.views.majority_judgment_vote_view import MajorityJudgmentVoteView
from apps.votes_results.views.single_option_vote_view import SingleOptionVoteView
from sesame.utils import get_user, get_token

def PollSearchView(request:HttpRequest):

    token_string: str = request.GET.get('tokens')
    searchpolltoken: PollTokens = PollTokens.objects.get(token_user=get_user(request_or_sesame=token_string))
    
    if searchpolltoken:
        return HttpResponseRedirect(reverse('apps.votes_results:vote', args=(searchpolltoken.poll_fk.id)))
    else:
        return render(request, 'polls_management/token_poll_redirect.html', {'poll': poll, 'tokennotfound':True })