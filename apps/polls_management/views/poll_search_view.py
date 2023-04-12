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



def PollSearchView(request:HttpRequest, poll_id):

    token_string: str = request.GET.get('token')
    poll_ids = PollModel.objects.all().values_list('id', flat=True)
    user_list = User.objects.all()
    tempuser: User = None
    temp: str = ""
    tempid: int = 0

    #find the id and the user of the token
    for x in poll_ids:
        for y in user_list:
            temp = get_token(user=y, scope=f"Poll:{x}")
            if (temp==token_string):
                tempid = x
                tempuser = y

    #check if the tempid is empty(=0) or full(!=0)
    if (tempid!=0):
        poll: PollModel = PollModel.objects.get(id=tempid)
        searchpolltoken: PollTokens = PollTokens.objects.get(token_user=tempuser, poll_fk=poll)

        if searchpolltoken:
            # token validation checks
            if TokenValidation.validate(searchpolltoken):
                request.session['token_used'] = searchpolltoken
                # redirect to proper vote method
                if poll.poll_type == PollModel.PollType.MAJORITY_JUDJMENT:
                    return HttpResponseRedirect(
                        reverse('apps.votes_results:majority_judgment_vote', args=(poll.id,)))
                else:
                    return HttpResponseRedirect(reverse(
                        'apps.votes_results:single_option_vote', 
                        args=(poll.id,)))
            elif TokenValidation.validate_mj_special_case(searchpolltoken):
                request.session['token_used'] = searchpolltoken
                # return HttpResponseRedirect(
                #     reverse('apps.votes_results:majority_judgment_vote', args=(poll.id,)))
                return render(request, 'polls_management/token_poll_redirect.html', {'poll': poll, 'mj_not_used': True})
            else:
                return render(request, 'polls_management/token_poll_redirect.html', {'poll': poll, 'tokennotfound':True })
        else:
            return render(request, 'polls_management/token_poll_redirect.html', {'poll': poll, 'tokennotfound':True })
    else:
        #problema: trovare pollid originale
        poll: PollModel = PollModel.objects.get(id=poll_id)
        return render(request, 'polls_management/token_poll_redirect.html', {'poll': poll, 'tokennotfound':False })