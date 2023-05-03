from django.http import Http404, HttpRequest, HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import render
from django.urls import reverse
from apps.polls_management.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.services.poll_service import PollService
from apps.votes_results.classes.poll_result import PollResult
from apps.votes_results.exceptions.results_not_available_exception import ResultsNotAvailableException
from apps.votes_results.services.single_option_vote_service import SingleOptionVoteService


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
        poll_results: PollResult = SingleOptionVoteService.calculate_result(poll_id, user=request.user)
    except PollDoesNotExistException:
        raise Http404
    except ResultsNotAvailableException:
        raise Http404

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
