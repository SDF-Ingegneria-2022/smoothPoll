from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.services.poll_service import PollService


def generic_results_view(request, poll_id: int):
    """Redirect to poll's main vote method's results"""
    
    try:
        # Retrieve poll
        poll: PollModel = PollService.get_poll_by_id(poll_id)
    except Exception:
        raise Http404(f"Poll with id {poll_id} not found.")
    
    # redirect to proper vote method's results
    if poll.poll_type == PollModel.PollType.MAJORITY_JUDJMENT:
        return HttpResponseRedirect(reverse('apps.votes_results:majority_judgment_results', args=(poll_id,)))
    
    if poll.poll_type == PollModel.PollType.SCHULZE:
        return HttpResponseRedirect(reverse('apps.votes_results:schulze_method_results', args=(poll_id,)))
    
    return HttpResponseRedirect(reverse('apps.votes_results:single_option_results', args=(poll_id,)))