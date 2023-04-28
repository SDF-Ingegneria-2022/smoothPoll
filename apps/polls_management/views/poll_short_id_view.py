from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.core.exceptions import ObjectDoesNotExist
from apps.polls_management.classes.poll_token_validation.token_validation import TokenValidation
from apps.polls_management.constants.template_path_constants import POLL_DETAILS_PAGE_TEMPLATE_PATH
from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.models.poll_token import PollTokens
from sesame.utils import get_user
from apps.votes_results.classes.vote.is_user_allowed_checker import is_user_allowed_factory

from apps.votes_results.classes.vote.vote_template_names import nonauth_user_template_name

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
        
        # todo: find a more explicit way to check if votation ended
        if poll.is_closed():
            return HttpResponseRedirect(reverse(
                'apps.votes_results:results', args=(poll.id,)))
        
        # (eventually) extract token for first time
        if poll.is_votable_token():
            try:
                short_token: PollTokens = PollTokens.objects.get(
                    token_user=get_user(
                        request_or_sesame=request, 
                        scope=f"Poll:{poll.id}"
                    ))
                request.session['token_used'] = short_token
            except Exception:
                return render(request, 'polls_management/token_poll_redirect.html', {'poll': poll})

        is_user_allowed_checker = is_user_allowed_factory(request, poll)

        # check user is generally allowed to access this poll 
        if not is_user_allowed_checker.is_user_allowed():
            return render(request, 
                nonauth_user_template_name(poll), 
                { 'poll': poll, })
        
        # check user is generally allowed to vote w this specific method
        if not is_user_allowed_checker.is_user_allowed_for_votemethod(poll.poll_type):
            return render(request, 
                nonauth_user_template_name(poll), 
                {
                    'poll': poll, 
                    'mj_not_used': poll.is_votable_w_so_and_mj() and \
                            is_user_allowed_checker.is_voted_so_but_not_mj() 
                })
        
        # todo: find a more explicit way to check if votation has not started
        if not poll.is_open():
            return render(request, 
                      POLL_DETAILS_PAGE_TEMPLATE_PATH,
                      {'poll': poll}
                      )
        
        # redirect to vote page (whatever is appropriate now)
        return HttpResponseRedirect(reverse(
            'apps.votes_results:vote', args=(poll.id,)))


    # def get(self, request, poll_short_id):
    #     """ Retuns a poll details page. Or a 404 error if the poll does not exist.
    #         If the poll is open and of type SINGLE_OPTION, redirects to the single option vote page, else
    #         if the poll is open and of type MAJORITY_JUDJMENT, redirects to the majority judgment vote page.
    #         If the poll is closed, returns the poll details page.
    #     """
    #     try:
    #         poll: PollModel = PollModel.objects.get(short_id=poll_short_id)
    #     except ObjectDoesNotExist:
    #         raise Http404()
        
    #     if poll.is_open() and not poll.is_closed():
    #         # check if a short link with token is used
    #         if poll.is_votable_token():
    #             try:
    #                 short_token: PollTokens = PollTokens.objects.get(token_user=get_user(request_or_sesame=request, scope=f"Poll:{poll.id}"))
    #                 request.session['token_used'] = short_token
    #             except Exception:
    #                 return render(request, 'polls_management/token_poll_redirect.html', {'poll': poll})
                
    #             # token validation checks
    #             if TokenValidation.validate(short_token):
    #                 request.session['token_used'] = short_token
    #                 # redirect to proper vote method
    #                 if poll.poll_type == PollModel.PollType.MAJORITY_JUDJMENT:
    #                     return HttpResponseRedirect(
    #                         reverse('apps.votes_results:majority_judgment_vote', args=(poll.id,)))
    #                 else:
    #                     return HttpResponseRedirect(reverse(
    #                         'apps.votes_results:single_option_vote', 
    #                         args=(poll.id,)))
    #             elif TokenValidation.validate_mj_special_case(short_token):
    #                     request.session['token_used'] = short_token
    #                     # return HttpResponseRedirect(
    #                     #     reverse('apps.votes_results:majority_judgment_vote', args=(poll.id,)))
    #                     return render(request, 'polls_management/token_poll_redirect.html', {'poll': poll, 'mj_not_used': True})
    #             else:
    #                     return render(request, 'polls_management/token_poll_redirect.html', {'poll': poll})

    #             # # TODO: find a way to remove the temporary logged user from the page of invalid tokens
    #             # # token validation controls
    #             # if PollTokenService.is_single_option_token_used(short_token) and not poll.is_votable_w_so_and_mj():
    #             #     # logout(request)
    #             #     return render(request, 'polls_management/token_poll_redirect.html', {'poll': poll})
    #             # elif PollTokenService.is_single_option_token_used(short_token) and poll.is_votable_w_so_and_mj() and not PollTokenService.is_majority_token_used(short_token):
    #             #     # pass the token to specific poll type view for vote
    #             #     request.session['token_used'] = short_token
    #             #     return HttpResponseRedirect(
    #             #         reverse('apps.votes_results:majority_judgment_vote', args=(poll.id,)))
    #             # elif PollTokenService.is_single_option_token_used(short_token) and poll.is_votable_w_so_and_mj() and PollTokenService.is_majority_token_used(short_token):
    #             #     # logout(request)
    #             #     return render(request, 'polls_management/token_poll_redirect.html', {'poll': poll})
    #             # elif PollTokenService.is_majority_token_used(short_token) and not poll.is_votable_w_so_and_mj():
    #             #     # logout(request)
    #             #     return render(request, 'polls_management/token_poll_redirect.html', {'poll': poll})
    #             # request.session['token_used'] = short_token
    #             # # redirect to proper vote method
    #             # if poll.poll_type == PollModel.PollType.MAJORITY_JUDJMENT:
    #             #     return HttpResponseRedirect(
    #             #         reverse('apps.votes_results:majority_judgment_vote', args=(poll.id,)))
    #             # else:
    #             #     return HttpResponseRedirect(reverse(
    #             #         'apps.votes_results:single_option_vote', 
    #             #         args=(poll.id,)))
    #         elif poll.is_votable_google():
    #             if request.user.is_authenticated:
    #                 # redirect to proper vote method
    #                 if poll.poll_type == PollModel.PollType.MAJORITY_JUDJMENT:
    #                     return HttpResponseRedirect(
    #                         reverse('apps.votes_results:majority_judgment_vote', args=(poll.id,)))
    #                 else:
    #                     return HttpResponseRedirect(reverse(
    #                         'apps.votes_results:single_option_vote', 
    #                         args=(poll.id,)))
    #             else:
    #                 return render(request, 'global/login.html', {'poll': poll})
    #         else:

    #         return HttpResponseRedirect(reverse('apps.votes_results:vote', args=(poll.id,)))
        
    #     elif poll.is_closed():
    #         return HttpResponseRedirect(reverse('apps.votes_results:results', args=(poll.id,)))

        
    #     return render(request, 
    #                   POLL_DETAILS_PAGE_TEMPLATE_PATH,
    #                   {'poll': poll}
    #                   )