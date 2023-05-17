import random
from typing import List
from django.http import Http404, HttpRequest, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from apps.polls_management.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.models.poll_option_model import PollOptionModel
from apps.polls_management.models.schulze_vote_model import SchulzeVoteModel
from apps.polls_management.services.poll_service import PollService
from apps.votes_results.classes.schulze_results.i_schulze_results import ISchulzeResults
from apps.votes_results.exceptions.poll_not_yet_voted_exception import PollNotYetVodedException
from apps.votes_results.exceptions.results_not_available_exception import ResultsNotAvailableException

class ShulzeResultsStub(ISchulzeResults):

    def __init__(self, poll: PollModel) -> None:
        super().__init__(poll)

    def calculate(self) -> None:

        options = self.poll.options()
        random.shuffle(options)
        self.__options = [[o] for o in options]

        self.__votes = []

    def get_votes(self) -> List[SchulzeVoteModel]:
        return self.__votes
        

    def get_sorted_options(self) -> List[List[PollOptionModel]]:
        return self.__options


def schulze_method_results_view(request: HttpRequest, poll_id: int):
    """Render Poll Schulze results"""

    # Poll should be Majority type
    try:
        poll = PollService.get_poll_by_id(poll_id)
    except PollDoesNotExistException:
        raise Http404()

    # Redirect to details page if poll is not yet open
    if not poll.is_open():
        return HttpResponseRedirect(reverse('apps.polls_management:poll_details', args=(poll_id,)))

    if poll.poll_type != PollModel.PollType.SCHULZE:
        raise Http404()
    
    try:
        # todo: replace with real call to service
        poll_results: ISchulzeResults = ShulzeResultsStub(poll)
        poll_results.calculate()
    except PollDoesNotExistException:
        raise Http404()
    except ResultsNotAvailableException:
        raise Http404
    except PollNotYetVodedException:
        poll_results = None

    return render(request, 'votes_results/schulze_method_results.html', {
        'poll_results': poll_results, 
        'poll': poll,
        'poll_info_to_view': {
            'name': False,
            'question': False,
            'choices': False,
            'status': True,
            'datetimes': True,
            'type': True,
        }
        })
