from polls.classes.poll_form import PollForm
from polls.models.poll_option_model import PollOptionModel
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

def create_poll_start(request: HttpRequest):
    return HttpResponseRedirect(reverse('polls:create-poll-1'))

def create_poll_step_1_view(request: HttpRequest):
    """View to handle step 1 of poll creation"""

    form = PollForm(request.POST or None, request.FILES or None)

    if request.method == "GET":
        return render(request, "polls/create_poll_step_1.html", {"form": form})
    
    if not form.is_valid():
        return HttpResponseRedirect(reverse('polls:create-poll-1'))

    form.save()
    #request.session['form-poll-id'] = form.id

    # PollOptionModel(value="Opzione 1", poll_fk=form.id).save()
    # PollOptionModel(value="Opzione 2", poll_fk=form.id).save()

    return HttpResponseRedirect(reverse('polls:create-poll-2'))

def create_poll_step_2_view(request: HttpRequest):
    """View to handle step 2 of poll creation"""

    # poll_id = request.session.get("form-poll-id")
    # if poll_id is None:
    #     HttpResponseRedirect(reverse('polls:create-poll'))

    # actual_options = PollOptionModel.objects.filter(poll_fk=poll_id).all()

    if request.method == "GET":
        return render(request, "polls/create_poll_step_2.html")


    return HttpResponseRedirect(reverse('polls:all_polls', kwargs={'page':1}))

