from polls.classes.poll_form import PollForm
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse


def create_poll_view(request: HttpRequest):
    """View to handle creation of a poll"""

    form = PollForm(request.POST or None, request.FILES or None)

    if request.method == "GET":
        return render(request, "polls/poll_create.html", {"form": form})
    
    if not form.is_valid():
        return HttpResponseRedirect(reverse('polls:create-poll'))

    form.save()

    # todo: change redirect to handle better the list 
    # a "last" page option would be useful
    return HttpResponseRedirect(reverse('polls:all_polls', kwargs={'page':1}))


