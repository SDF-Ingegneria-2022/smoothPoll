from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from apps.polls_management.classes.poll_token_validation.token_validation import TokenValidation
from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.services.poll_service import PollService
from apps.polls_management.services.poll_token_service import PollTokenService

def generic_vote_view(request, poll_id: int):
    """Redirect to poll's main vote method"""

    try:
        # Retrieve poll
        poll: PollModel = PollService.get_poll_by_id(poll_id)
    except Exception:
        raise Http404(f"Poll with id {poll_id} not found.")
    
    # add control if poll is votable only with tokens
    if poll.is_votable_token():
        try:
            token_poll_data = PollTokenService.get_poll_token_by_user(request.user)
        except Exception:
            return render(request, 'polls_management/token_poll_redirect.html', {'poll': poll})
        
        # token validation checks
        if TokenValidation.validate(token_poll_data):
            request.session['token_used'] = token_poll_data
            # redirect to proper vote method
            if poll.poll_type == PollModel.PollType.MAJORITY_JUDJMENT:
                return HttpResponseRedirect(
                    reverse('apps.votes_results:majority_judgment_vote', args=(poll.id,)))
            else:
                return HttpResponseRedirect(reverse(
                    'apps.votes_results:single_option_vote', 
                    args=(poll.id,)))
        elif TokenValidation.validate_mj_special_case(token_poll_data):
            request.session['token_used'] = token_poll_data
            # return HttpResponseRedirect(
            #     reverse('apps.votes_results:majority_judgment_vote', args=(poll.id,)))
            return render(request, 'polls_management/token_poll_redirect.html', {'poll': poll, 'mj_not_used': True})

        else:
            return render(request, 'polls_management/token_poll_redirect.html', {'poll': poll})
        
        # TODO: find a way to remove the temporary logged user from the page of invalid tokens
        # token validation controls
        # if PollTokenService.is_single_option_token_used(token_poll_data) and not poll.is_votable_w_so_and_mj():
        #     # logout(request)
        #     return render(request, 'polls_management/token_poll_redirect.html', {'poll': poll})
        # elif PollTokenService.is_single_option_token_used(token_poll_data) and poll.is_votable_w_so_and_mj() and not PollTokenService.is_majority_token_used(token_poll_data):
        #     # pass the token to specific poll type view for vote
        #     request.session['token_used'] = token_poll_data
        #     return HttpResponseRedirect(
        #         reverse('apps.votes_results:majority_judgment_vote', args=(poll_id,)))
        # elif PollTokenService.is_single_option_token_used(token_poll_data) and poll.is_votable_w_so_and_mj() and PollTokenService.is_majority_token_used(token_poll_data):
        #     # logout(request)
        #     return render(request, 'polls_management/token_poll_redirect.html', {'poll': poll})
        # elif PollTokenService.is_majority_token_used(token_poll_data) and not poll.is_votable_w_so_and_mj():
        #     # logout(request)
        #     return render(request, 'polls_management/token_poll_redirect.html', {'poll': poll})
        
        # # pass the token to specific poll type view for vote
        # request.session['token_used'] = token_poll_data

    elif poll.is_votable_google():
        if request.user.is_authenticated:
            # redirect to proper vote method
            if poll.poll_type == PollModel.PollType.MAJORITY_JUDJMENT:
                return HttpResponseRedirect(
                    reverse('apps.votes_results:majority_judgment_vote', args=(poll_id,)))
            else:
                return HttpResponseRedirect(reverse(
                    'apps.votes_results:single_option_vote', 
                    args=(poll_id,)))
        else:
            return render(request, 'global/login.html', {'poll': poll})

    else:
        # redirect to proper vote method
        if poll.poll_type == PollModel.PollType.MAJORITY_JUDJMENT:
            return HttpResponseRedirect(
                reverse('apps.votes_results:majority_judgment_vote', args=(poll_id,)))
        else:
            return HttpResponseRedirect(reverse(
                'apps.votes_results:single_option_vote', 
                args=(poll_id,)))