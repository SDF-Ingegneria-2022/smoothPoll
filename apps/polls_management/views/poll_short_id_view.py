from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.core.exceptions import ObjectDoesNotExist
from apps.polls_management.constants.template_path_constants import POLL_DETAILS_PAGE_TEMPLATE_PATH
from apps.polls_management.models.poll_model import PollModel
from apps.votes_results.views.majority_judgment_vote_view import MajorityJudgmentVoteView
from apps.votes_results.views.single_option_vote_view import SingleOptionVoteView

class PollShortIdView(View):
    def get(self, request, poll_short_id):
        """ Retuns a poll details page. Or a 404 error if the poll does not exist.
            If the poll is open and of type SINGLE_OPTION, redirects to the single option vote page, else
            if the poll is open and of type MAJORITY_JUDJMENT, redirects to the majority judgment vote page.
            If the poll is closed, returns the poll details page.
        """
        try:
            poll: PollModel = PollModel.objects.get(short_id=poll_short_id)
        except ObjectDoesNotExist:
            raise Http404()
        
        if poll.is_open() and not poll.is_closed():
            return HttpResponseRedirect(reverse('apps.votes_results:vote', args=(poll.id,)))

        
        return render(request, 
                      POLL_DETAILS_PAGE_TEMPLATE_PATH,
                      {'poll': poll}
                      )