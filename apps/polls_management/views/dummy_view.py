from typing import List
from django.http import Http404  
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseServerError, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
from apps.polls_management.classes.majority_poll_result_data import MajorityPollResultData
from apps.polls_management.classes.poll_result import PollResult, PollResultVoice
from apps.polls_management.classes.poll_result import PollResult
from apps.polls_management.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
from apps.polls_management.exceptions.poll_option_rating_unvalid_exception import PollOptionRatingUnvalidException
from apps.polls_management.exceptions.vote_does_not_exixt_exception import VoteDoesNotExistException
from apps.polls_management.models.majority_vote_model import MajorityVoteModel
from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.models.poll_option_model import PollOptionModel
from apps.votes_results.services.majority_judjment_vote_service import MajorityJudjmentVoteService
from apps.polls_management.services.poll_service import PollService
from apps.polls_management.exceptions.poll_option_unvalid_exception import PollOptionUnvalidException
from apps.votes_results.services.single_option_vote_service import SingleOptionVoteService

def all_polls(request: HttpRequest):
    """
    Render page with all polls.
    """
    try:
        page_information: str = request.GET.get('page')
        per_page: int = int(request.GET.get('per_page'))
    except TypeError:
        page_information = '1'
        per_page = 10
    
    paginator: Paginator = PollService.get_paginated_polls(per_page)

    if page_information == 'last':
        page = paginator.num_pages
    else:
        page: int = int(page_information)

    # session variables for modal toggle of delete poll result
    delete_success = request.session.get('delete_success')
    delete_error = request.session.get('delete_error')

    # session variable for edit alert message
    not_editable = request.session.get('cannot_edit')

    if delete_success:
        del request.session['delete_success']

    if delete_error:
        del request.session['delete_error']

    if not_editable:
        del request.session['cannot_edit']
    
    return render(  request, 
                    'polls_management/all_polls.html', 
                    {
                    'per_page': per_page,
                    'page': paginator.page(page),
                    'delete_success': delete_success,
                    'delete_error': delete_error,
                    'cannot_edit': not_editable
                    }
                )

