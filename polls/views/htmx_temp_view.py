from typing import List
from django.http import Http404  
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseServerError, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
from polls.classes.majority_poll_result_data import MajorityPollResultData
from polls.classes.poll_result import PollResult, PollResultVoice
from polls.classes.poll_result import PollResult
from polls.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
from polls.exceptions.poll_option_rating_unvalid_exception import PollOptionRatingUnvalidException
from polls.exceptions.vote_does_not_exixt_exception import VoteDoesNotExistException
from polls.models.majority_vote_model import MajorityVoteModel
from polls.models.poll_model import PollModel
from polls.models.poll_option_model import PollOptionModel
from polls.services.majority_vote_service import MajorityVoteService
from polls.services.poll_service import PollService
from polls.exceptions.poll_option_unvalid_exception import PollOptionUnvalidException
from polls.services.vote_service import VoteService


def htmx_example_page(request: HttpRequest, poll_id: int):

    try:
        poll = PollService.get_poll_by_id(poll_id)
    except PollDoesNotExistException:
        raise Http404()

    return render(request, 'polls/create_poll_htmx.html', {
        'options': poll.options(), 
        'poll': poll, 
    })

def htmx_create_option(request: HttpRequest, poll_id: str):

    try:
        poll = PollService.get_poll_by_id(poll_id)
    except PollDoesNotExistException:
        raise Http404()

    return render(request, 'polls/components/htmx_option_input.html', {
        "option": poll.options()[0], 
        'poll': poll, 
    })

def htmx_delete_option(request: HttpRequest, poll_id: str, option_id: int):
    return HttpResponse("")


def htmx_edit_option(request: HttpRequest, poll_id: str, option_id: int):
    print(request.POST)
    return HttpResponse("")