from typing import List
from django.http import Http404, HttpRequest, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from apps.polls_management.exceptions.poll_does_not_exist_exception import PollDoesNotExistException

from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.services.poll_service import PollService
from apps.votes_results.classes.majority_judgment_results.i_majority_judment_results import IMajorityJudgmentResults
from apps.votes_results.classes.majority_poll_result_data import MajorityPollResultData
from apps.votes_results.exceptions.poll_not_yet_voted_exception import PollNotYetVodedException
from apps.votes_results.exceptions.results_not_available_exception import ResultsNotAvailableException
from apps.votes_results.services.majority_judgment_vote_service import MajorityJudjmentVoteService


def majority_judgment_results_view(request: HttpRequest, poll_id: int):
    """Render page with majority poll results"""

    # Poll should be Majority type
    try:
        poll = PollService.get_poll_by_id(poll_id)
    except PollDoesNotExistException:
        raise Http404()

    # Redirect to details page if poll is not yet open
    if not poll.is_open():
        return HttpResponseRedirect(reverse('apps.polls_management:poll_details', args=(poll_id,)))

    if ((poll.poll_type == PollModel.PollType.SINGLE_OPTION) or \
        (poll.poll_type == PollModel.PollType.SCHULZE)) and not poll.is_votable_w_so_and_mj():
        raise Http404()
    
    try:    
        poll_results: IMajorityJudgmentResults = \
            MajorityJudjmentVoteService.calculate_result(
            poll_id=str(poll_id), user=request.user)
    
    except PollDoesNotExistException:
        raise Http404()
    except ResultsNotAvailableException:
        raise Http404
    except PollNotYetVodedException:
        poll_results = None

    return render(request, 'votes_results/majority_judgment_results.html', {
        'poll_results': poll_results, 
        'poll': PollModel.objects.get(id=poll_id),
        'poll_info_to_view': {
            'name': False,
            'question': False,
            'choices': False,
            'status': True,
            'datetimes': True,
            'type': True,
        }
        })
