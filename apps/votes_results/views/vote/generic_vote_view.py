from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from apps.polls_management.classes.poll_token_validation.token_validation import TokenValidation
from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.services.poll_service import PollService
from apps.polls_management.services.poll_token_service import PollTokenService
from apps.votes_results.classes.vote.is_user_allowed_checker import is_user_allowed_factory
from apps.votes_results.classes.vote.vote_template_names import nonauth_user_template_name

def generic_vote_view(request, poll_id: int):
    """Redirect to poll's main vote method"""

    try:
        # Retrieve poll
        poll: PollModel = PollService.get_poll_by_id(poll_id)
    except Exception:
        raise Http404(f"Poll with id {poll_id} not found.")
    
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
    
    # redirect to majority judgment vote view or single option
    if poll.poll_type == PollModel.PollType.MAJORITY_JUDJMENT:
        return HttpResponseRedirect(
            reverse('apps.votes_results:majority_judgment_vote', 
                    args=(poll_id,)))

    return HttpResponseRedirect(reverse(
        'apps.votes_results:single_option_vote', 
        args=(poll_id,)))


    # add control if poll is votable only with tokens
    # if poll.is_votable_token():
    #     try:
    #         token_poll_data = PollTokenService.get_poll_token_by_user(request.user)
    #     except Exception:
    #         return render(request, 'polls_management/token_poll_redirect.html', {'poll': poll})
        
    #     # token validation checks
    #     if TokenValidation.validate(token_poll_data):
    #         request.session['token_used'] = token_poll_data
    #         # redirect to proper vote method
    #         if poll.poll_type == PollModel.PollType.MAJORITY_JUDJMENT:
    #             return HttpResponseRedirect(
    #                 reverse('apps.votes_results:majority_judgment_vote', args=(poll.id,)))
    #         else:
    #             return HttpResponseRedirect(reverse(
    #                 'apps.votes_results:single_option_vote', 
    #                 args=(poll.id,)))
    #     elif TokenValidation.validate_mj_special_case(token_poll_data):
    #         request.session['token_used'] = token_poll_data
    #         # return HttpResponseRedirect(
    #         #     reverse('apps.votes_results:majority_judgment_vote', args=(poll.id,)))
    #         return render(request, 'polls_management/token_poll_redirect.html', {'poll': poll, 'mj_not_used': True})

    #     else:
    #         return render(request, 'polls_management/token_poll_redirect.html', {'poll': poll})


    # elif poll.is_votable_google():
    #     if request.user.is_authenticated:
    #         # redirect to proper vote method
    #         if poll.poll_type == PollModel.PollType.MAJORITY_JUDJMENT:
    #             return HttpResponseRedirect(
    #                 reverse('apps.votes_results:majority_judgment_vote', args=(poll_id,)))
    #         else:
    #             return HttpResponseRedirect(reverse(
    #                 'apps.votes_results:single_option_vote', 
    #                 args=(poll_id,)))
    #     else:
    #         return render(request, 'global/login.html', {'poll': poll})

    # else:
    #     # redirect to proper vote method
    #     if poll.poll_type == PollModel.PollType.MAJORITY_JUDJMENT:
    #         return HttpResponseRedirect(
    #             reverse('apps.votes_results:majority_judgment_vote', args=(poll_id,)))
    #     else:
    #         return HttpResponseRedirect(reverse(
    #             'apps.votes_results:single_option_vote', 
    #             args=(poll_id,)))
