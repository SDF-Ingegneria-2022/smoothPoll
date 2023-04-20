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
from apps.polls_management.classes.poll_token_validation.token_validation import TokenValidation
from sesame.utils import get_user, get_token
from django.contrib.auth.models import User



def PollCloseView(request:HttpRequest, poll_id):

    try:
        PollService.close_poll(poll_id)
    except Exception:
        raise Http404(f"Poll with id {poll_id} not found")

    return render(request, 'votes_results/poll_details.html', {'poll': poll })