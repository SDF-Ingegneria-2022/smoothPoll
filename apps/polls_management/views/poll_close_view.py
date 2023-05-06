from django.http import Http404, HttpResponseRedirect, HttpRequest
from django.urls import reverse
from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.services.poll_service import PollService
from django.views import View
from django.core.exceptions import PermissionDenied

class ClosePollView(View):
    # Todo; change to post method after refactoring
    def get(self, request, poll_id):
        
        try:
            # Retrieve poll
            poll: PollModel = PollService.get_poll_by_id(poll_id)
             
        except Exception:
            raise Http404(f"Poll with id {poll_id} not found.")
        
            
        if request.user == poll.author and poll.is_open:
            PollService.close_poll(poll_id)
        else: 
            raise PermissionDenied(f"Poll with id {poll_id} not found.")
       
        return HttpResponseRedirect(reverse('apps.polls_management:poll_details', args=(poll_id,)))