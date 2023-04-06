from apps.polls_management.classes.poll_token_validation.token_validation import TokenValidation
from apps.polls_management.models.poll_token import PollTokens
from apps.polls_management.services.poll_token_service import PollTokenService
from apps.votes_results.classes.poll_result import PollResult
from apps.votes_results.classes.poll_result import PollResult
from apps.polls_management.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
from apps.votes_results.exceptions.vote_does_not_exixt_exception import VoteDoesNotExistException
from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.services.poll_service import PollService
from apps.votes_results.exceptions.poll_option_unvalid_exception import PollOptionUnvalidException
from apps.votes_results.classes.single_option_vote_counter import SingleOptionVoteCounter
from apps.votes_results.services.single_option_vote_service import SingleOptionVoteService

from django.http import Http404  
from django.http import HttpRequest, HttpResponseServerError, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from sesame.utils import get_user, get_token
from sesame.decorators import authenticate


REQUEST_VOTE = 'vote'

SESSION_SINGLE_OPTION_VOTE_SUBMIT_ERROR = 'vote-submit-error'
SESSION_SINGLE_OPTION_VOTE_ID = 'single-option-vote-id'
SESSION_TOKEN_USED = 'token_used'

class SingleOptionVoteView(View):
    """View to handle Single Option vote operation. """

    def get(self, request: HttpRequest, poll_id: int, *args, **kwargs):
        """Render the form wich permits user to vote"""

        try:
            # Retrieve poll
            poll: PollModel = PollService.get_poll_by_id(poll_id)
        except Exception:
            raise Http404(f"Poll with id {poll_id} not found.")

        # redirect to details page if poll is not yet open
        if not poll.is_open() or poll.is_closed():
            return render(request, 'votes_results/poll_details.html', {'poll': poll})
        
        # check if the poll is accessed by a single poll url rather than the link with the token
        # and control of token validity
        if poll.is_votable_token():
            if request.session.get(SESSION_TOKEN_USED) is None:
                return render(request, 'polls_management/token_poll_redirect.html', {'poll': poll})
            else:
                try:
                    token_poll = request.session.get(SESSION_TOKEN_USED)
                except Exception:
                    raise Http404(f"Token associated with user {token_poll.token_user} not found.")

                if not TokenValidation.validate(token_poll) and not poll.votable_mj:
                    return render(request, 'polls_management/token_poll_redirect.html', {'poll': poll})
                
                elif poll.votable_mj:
                    # check special token case with votable mj
                    if not TokenValidation.validate(token_poll):
                        if TokenValidation.validate_mj_special_case(token_poll):
                            # pass the token to specific poll type view for vote
                            request.session[SESSION_TOKEN_USED] = token_poll
                            return HttpResponseRedirect(reverse('apps.votes_results:majority_judgment_vote', args=(poll_id,)))
                        else:
                            return render(request, 'polls_management/token_poll_redirect.html', {'poll': poll})
                        
        elif poll.is_votable_google:
            if not request.user.is_authenticated:
                return render(request, 'global/login.html')
            elif PollTokens.objects.filter(token_user=request.user, poll_fk=poll).exists():
                google_token = PollTokens.objects.get(token_user=request.user, poll_fk=poll)
                if not TokenValidation.validate(google_token) and not poll.votable_mj:
                    return render(request, 'global/login.html')
                elif poll.votable_mj:
                    # check special token case with votable mj
                    if not TokenValidation.validate(google_token):
                        if TokenValidation.validate_mj_special_case(google_token):
                            return HttpResponseRedirect(reverse('apps.votes_results:majority_judgment_vote', args=(poll_id,)))
        
        if poll.poll_type == PollModel.PollType.MAJORITY_JUDJMENT:
            return HttpResponseRedirect(reverse('apps.votes_results:majority_judgment_vote', args=(poll_id,)))

        # Get eventual error message and clean it
        eventual_error = request.session.get(SESSION_SINGLE_OPTION_VOTE_SUBMIT_ERROR)
        if eventual_error is not None:
            del request.session[SESSION_SINGLE_OPTION_VOTE_SUBMIT_ERROR]
        
        # Render vote form (with eventual error message)
        return render(request, 
                    'votes_results/single_option_vote.html', 
                    { 
                        'poll': poll, 
                        'error': eventual_error 
                    })

    def post(self, request: HttpRequest, poll_id: int, *args, **kwargs):
        """Handle vote perform and redirect to recap (or 
        redirect to form w errors)"""

        try:
            # Retrieve poll
            poll: PollModel = PollService.get_poll_by_id(poll_id)
        except Exception:
            raise Http404(f"Poll with id {poll_id} not found.")

        # redirect to details page if poll is not yet open
        if not poll.is_open() or poll.is_closed():
            return HttpResponseRedirect(reverse('apps.polls_management:poll_details', args=(poll_id,)))

        # check if there is an attempt to vote with a token already used
        if poll.is_votable_token() and request.session.get(SESSION_TOKEN_USED) is not None:
            try:
                token_poll_data = request.session.get(SESSION_TOKEN_USED)
                updated_token = PollTokenService.get_poll_token_by_user(token_poll_data.token_user)
            except Exception:
                return render(request, 'polls_management/token_poll_redirect.html', {'poll': poll})

            if not TokenValidation.validate(updated_token):
                return render(request, 'polls_management/token_poll_redirect.html', {'poll': poll})
            
        elif poll.is_votable_google:
            if PollTokens.objects.filter(token_user=request.user, poll_fk=poll).exists():
                google_token = PollTokens.objects.get(token_user=request.user, poll_fk=poll)
                if not TokenValidation.validate(google_token):
                    return render(request, 'global/login.html')

        # Check is passed any data.
        if REQUEST_VOTE not in request.POST:
            request.session[SESSION_SINGLE_OPTION_VOTE_SUBMIT_ERROR] = "Errore! Per confermare la scelta " \
                + "devi esprimere una preferenza."
            return HttpResponseRedirect(reverse('apps.votes_results:single_option_vote', args=(poll_id,)))

        # Save vote preference in session
        request.session[SESSION_SINGLE_OPTION_VOTE_ID] = request.POST[REQUEST_VOTE]
        
        # Perform vote and handle missing vote or poll exception.
        try:
            vote = SingleOptionVoteService.perform_vote(poll_id, request.POST[REQUEST_VOTE])

            # invalidation of token if vote is successful
            if poll.is_votable_token and request.session.get(SESSION_TOKEN_USED) is not None:
                try:
                    token_poll = request.session.get(SESSION_TOKEN_USED)
                    PollTokenService.check_single_option(token_poll)
                except Exception:
                    raise Http404(f"Token associated with user {token_poll.token_user} not found.")
            
            elif poll.is_votable_google:
                PollTokenService.create_google_record(request.user, poll)

        except PollOptionUnvalidException:
            request.session[SESSION_SINGLE_OPTION_VOTE_SUBMIT_ERROR] = "Errore! La scelte deve essere " \
                + "espressa tramite l'apposito form. Se continui a vedere questo " \
                + "messaggio contatta gli sviluppatori."
            return HttpResponseRedirect(reverse('apps.votes_results:single_option_vote', args=(poll_id,)))
        except PollDoesNotExistException:
            raise Http404

        # Clean eventual error session.
        if request.session.get(SESSION_SINGLE_OPTION_VOTE_SUBMIT_ERROR) is not None:
            del request.session[SESSION_SINGLE_OPTION_VOTE_SUBMIT_ERROR]

        # Save user vote in session (so when I re-render with GET I have the vote).
        request.session['vote-submit-id'] = vote.id

        # RE-direct to get request.
        return HttpResponseRedirect(reverse('apps.votes_results:single_option_recap', args=(poll_id, ))) 

    
def single_option_recap_view(request: HttpRequest, poll_id: int): 
    """Submit the vote.
    Args:
        request (HttpRequest): Request object.
        poll_id (int): The poll id.
    Returns:
        HttpResponseRedirect: Redirect to the poll page.
        HttpResponse: Rendered confirm page.
    """

    # GET REQUEST --> I wanna render a page wich shows performed vote
    # (reloadable as many times user wants)

    try:
        # Retrieve poll
        poll: PollModel = PollService.get_poll_by_id(poll_id)
    except Exception:
        raise Http404(f"Poll with id {poll_id} not found.")

    # redirect to details page if poll is not yet open
    if not poll.is_open() or poll.is_closed():
        return HttpResponseRedirect(reverse('apps.polls_management:poll_details', args=(poll_id,)))

    # Retrieve session saved vote ID
    vote_id = request.session.get("vote-submit-id")
    if vote_id is None:
        request.session[SESSION_SINGLE_OPTION_VOTE_SUBMIT_ERROR] = "Errore! Non hai ancora espresso " \
            + "nessuna scelta. Usa questo form per esprimere la tua preferenza."
        return HttpResponseRedirect(reverse('apps.votes_results:single_option_vote', args=(poll_id,)))

    # retrieve vote 
    try:
        vote = SingleOptionVoteService.get_vote_by_id(vote_id)
    except VoteDoesNotExistException:
        request.session[SESSION_SINGLE_OPTION_VOTE_SUBMIT_ERROR] = "Errore! Non hai ancora espresso " \
            + "nessuna scelta. Usa questo form per esprimere la tua preferenza."
        return HttpResponseRedirect(reverse('apps.votes_results:single_option_vote', args=(poll_id,)))
    
    # show confirm page
    mj_vote_counter: SingleOptionVoteCounter = None
    
    if poll.votable_mj:
        mj_vote_counter: SingleOptionVoteCounter = SingleOptionVoteCounter(poll)

    # Clean session data for token validation if poll is not also votable with majority
    # if not poll.votable_mj:
    #     if request.session.get(SESSION_TOKEN_USED) is not None:
    #         del request.session[SESSION_TOKEN_USED]
        
    return render(request, 'votes_results/single_option_recap.html', {'vote': vote,
                                                                      'mj_vote_counter': mj_vote_counter})


def single_option_results_view(request: HttpRequest, poll_id: int):
    """Render page with results.
    Args:
        request (HttpRequest): Request object.
        poll_id (int): The poll id.
    Returns:
        HttpResponse: Rendered results page.
        HttpResponseServerError: If DB is not initialized.
    """

    # if poll type is majority, we need to redirect 
    # to majority results page
    try:
        # Retrieve poll
        poll: PollModel = PollService.get_poll_by_id(poll_id)
    except Exception:
        raise Http404(f"Poll with id {poll_id} not found.")

    # redirect to details page if poll is not yet open
    if not poll.is_open():
        return HttpResponseRedirect(reverse('apps.polls_management:poll_details', args=(poll_id,)))

    if poll.poll_type == PollModel.PollType.MAJORITY_JUDJMENT:
        return HttpResponseRedirect(reverse('apps.votes_results:majority_judgment_results', args=(poll_id,)))

    # regular results page 
    try:
        poll_results: PollResult = SingleOptionVoteService.calculate_result(poll_id)
    except PollDoesNotExistException:
        raise Http404
    except Exception:
        # Internal error: you should inizialize DB first (error 500)
        return HttpResponseServerError("Something got (slighly) terribly wrong. Please contact developers")

    return render(request, 'votes_results/single_option_results.html', 
        {'poll_results': poll_results,
         'poll_info_to_view': {
            'name': False,
            'question': False,
            'choices': False,
            'status': True,
            'datetimes': True,
        }
         }
        )
