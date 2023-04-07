from typing import List
from django.http import HttpRequest
from django.shortcuts import render
from django.core.paginator import Paginator
from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.services.poll_service import PollService


SESSION_DELETE_SUCCESS = 'delete_success'
SESSION_DELETE_ERROR  = 'delete_error'
SESSION_CANNOT_EDIT   = 'cannot_edit'

def all_votable_polls(request: HttpRequest):
    """
    Render page with all polls.
    """
    try:
        page_information: str = request.GET.get('page')
        per_page: int = int(request.GET.get('per_page'))
    except TypeError:
        page_information = '1'
        per_page = 10
    
    userPolls: List[PollModel] = PollService.votable_or_closed_polls()
    paginator: Paginator = Paginator(userPolls, per_page)

    if page_information == 'last':
        page = paginator.num_pages
    else:
        page: int = int(page_information)

    # session variables for modal toggle of delete poll result
    delete_success = request.session.get(SESSION_DELETE_SUCCESS)
    delete_error = request.session.get(SESSION_DELETE_ERROR)

    # session variable for edit alert message
    not_editable = request.session.get(SESSION_CANNOT_EDIT)

    if delete_success:
        del request.session[SESSION_DELETE_SUCCESS]

    if delete_error:
        del request.session[SESSION_DELETE_ERROR]

    if not_editable:
        del request.session[SESSION_CANNOT_EDIT]
    
    return render(  request, 
                    'votes_results/vote_all_polls.html', 
                    {
                    'per_page': per_page,
                    'page': paginator.page(page),
                    'delete_success': delete_success,
                    'delete_error': delete_error,
                    'cannot_edit': not_editable
                    }
                )
