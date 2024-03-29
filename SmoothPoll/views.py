from django.http import Http404
from django.shortcuts import render
from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.services.poll_service import PollService

from apps.polls_management.views.poll_short_id_view import PollShortIdView
from apps.votes_results.classes.vote_consistency.check_consistency_session import CheckConsistencySession

# todo: remove this dependency 
from apps.votes_results.views.vote.majority_judgment_vote_view import SESSION_CONSISTENCY_CHECK
from apps.votes_results.views.vote.single_option_vote_view import SESSION_SINGLE_OPTION_VOTE_ID

def home(request):
    """
    App home page
    """
    predefined_polls = PollService.votable_or_closed_polls()

    # categorize polls by type 
    single_option_polls = [
        poll for poll in predefined_polls 
        if poll.poll_type == PollModel.PollType.SINGLE_OPTION
    ]

    majority_judgment_polls = [
        poll for poll in predefined_polls
        if poll.poll_type == PollModel.PollType.MAJORITY_JUDJMENT
    ]

    schulze_method_polls = [
        poll for poll in predefined_polls
        if poll.poll_type == PollModel.PollType.SCHULZE
    ]

    # consistency check session cleaning (?)

    check_consistency_session: CheckConsistencySession = CheckConsistencySession(request)
    check_consistency_session.clear_session([SESSION_SINGLE_OPTION_VOTE_ID, SESSION_CONSISTENCY_CHECK])

    return render(request, "global/home.html", {
        "single_option_polls": single_option_polls, 
        "majority_judgment_polls": majority_judgment_polls,
        "schulze_method_polls": schulze_method_polls
        })

def general_info(request):
    """General information page about poll methods"""
    return render(request, "global/info/general.html")

def single_option_info(request):
    """Info page for single option poll type"""
    return render(request, "global/info/single_option_info.html")

def majority_judgment_info(request):
    """Info page for majority judgment poll type"""
    return render(request, "global/info/majority_judgment_info.html")

def schulze_method_info(request):
    """Info page for schulze method poll type"""
    return render(request, "global/info/schulze_method_info.html")

def attributions(request):
    """Attributions for Creative Common material"""
    return render(request, "global/attributions.html")

def login_redirect_page(request):
    """Page to redirect to login when the user tries to do
    authentication-only procedures"""

    return render(request, 'global/login.html')

def error_404_view(request, exception):
    """
    Page 404 handler view. It is called when a page is not found.
    """
    return render(request, 'global/404.html')

def error_404_view_redirect(request):
    """
    Page 404 handler view redirect. It is called when a page is not found.
    """
    raise Http404()

def poll_details_page(request, poll_short_id):
    """
    Page to show the details of a poll.
    """
    return PollShortIdView.as_view()(request, poll_short_id)
    