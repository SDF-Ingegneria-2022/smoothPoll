from django.http import Http404
from django.shortcuts import render
from django.views import View
from django.core.exceptions import ObjectDoesNotExist
from apps.polls_management.constants.template_path_constants import POLL_DETAILS_PAGE_TEMPLATE_PATH
from apps.polls_management.models.poll_model import PollModel

class PollShortIdView(View):
    def get(self, request, poll_short_id):
        """Retuns a poll details page. Or a 404 error if the poll does not exist.
        """
        try:
            poll: PollModel = PollModel.objects.get(short_id=poll_short_id)
        except ObjectDoesNotExist:
            raise Http404()
        
        return render(request, 
                      POLL_DETAILS_PAGE_TEMPLATE_PATH,
                      {'poll': poll}
                      )