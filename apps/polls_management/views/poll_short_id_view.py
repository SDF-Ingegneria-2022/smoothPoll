from django.shortcuts import render
from django.views import View
from apps.polls_management.constants.template_path_constants import POLL_DETAILS_PAGE_TEMPLATE_PATH

class PollShortIdView(View):
    def get(self, request, poll_short_id):
        
        return render(request, "polls_management/poll_details_page.html")