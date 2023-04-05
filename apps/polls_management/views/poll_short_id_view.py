from django.http import Http404, HttpResponseRedirect
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

class PollShortIdView(View):
    def get(self, request, poll_short_id):
        """ Retuns a poll details page. Or a 404 error if the poll does not exist.
            If the poll is open and of type SINGLE_OPTION, redirects to the single option vote page, else
            if the poll is open and of type MAJORITY_JUDJMENT, redirects to the majority judgment vote page.
            If the poll is closed, returns the poll details page.
        """
        try:
            poll: PollModel = PollModel.objects.get(short_id=poll_short_id)
        except ObjectDoesNotExist:
            raise Http404()
        
        if poll.is_open() and not poll.is_closed():
            # check if a short link with token is used
            if poll.is_votable_token():
                try:
                    short_token: PollTokens = PollTokens.objects.get(token_user=get_user(request_or_sesame=request, scope=f"Poll:{poll.id}"))
                    token_poll_data = PollTokenService.get_poll_token_by_user(short_token.token_user)
                except Exception:
                    return render(request, 'polls_management/token_poll_redirect.html', {'poll': poll})
                
                # TODO: find a way to remove the temporary logged user from the page of invalid tokens
                # token validation controls
                if PollTokenService.is_single_option_token_used(token_poll_data) and not poll.votable_mj:
                    # logout(request)
                    return render(request, 'polls_management/token_poll_redirect.html', {'poll': poll})
                elif PollTokenService.is_single_option_token_used(token_poll_data) and poll.votable_mj and not PollTokenService.is_majority_token_used(token_poll_data):
                    # pass the token to specific poll type view for vote
                    request.session['token_used'] = token_poll_data
                    return HttpResponseRedirect(
                        reverse('apps.votes_results:majority_judgment_vote', args=(poll.id,)))
                elif PollTokenService.is_single_option_token_used(token_poll_data) and poll.votable_mj and PollTokenService.is_majority_token_used(token_poll_data):
                    # logout(request)
                    return render(request, 'polls_management/token_poll_redirect.html', {'poll': poll})
                elif PollTokenService.is_majority_token_used(token_poll_data) and not poll.votable_mj:
                    # logout(request)
                    return render(request, 'polls_management/token_poll_redirect.html', {'poll': poll})
                request.session['token_used'] = short_token
                # redirect to proper vote method
                if poll.poll_type == PollModel.PollType.MAJORITY_JUDJMENT:
                    return HttpResponseRedirect(
                        reverse('apps.votes_results:majority_judgment_vote', args=(poll.id,)))
                else:
                    return HttpResponseRedirect(reverse(
                        'apps.votes_results:single_option_vote', 
                        args=(poll.id,)))
            else:
                return HttpResponseRedirect(reverse('apps.votes_results:vote', args=(poll.id,)))
        elif poll.is_closed():
            return HttpResponseRedirect(reverse('apps.votes_results:results', args=(poll.id,)))

        
        return render(request, 
                      POLL_DETAILS_PAGE_TEMPLATE_PATH,
                      {'poll': poll}
                      )