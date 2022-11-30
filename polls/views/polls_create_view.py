from polls.classes.poll_form import PollForm
from polls.models.poll_option_model import PollOptionModel
from django.http import HttpRequest, HttpResponseRedirect, HttpResponse
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

    poll = form.save()
    request.session['form-poll-id'] = poll.id

    # PollOptionModel(value="Opzione 1", poll_fk=poll.id).save()
    # PollOptionModel(value="Opzione 2", poll_fk=poll.id).save()

    return HttpResponseRedirect(reverse('polls:create-poll-2'))

def create_poll_step_2_view(request: HttpRequest):
    """View to handle step 2 of poll creation"""

    poll_id = request.session.get("form-poll-id")
    if poll_id is None:
        HttpResponseRedirect(reverse('polls:create-poll'))

    if request.method == "GET":
        return render(request, "polls/create_poll_step_2.html")

    options = request.POST.getlist("options[]")
    
    if options is None:
        # todo: render error: add at least n-options
        # return HttpResponse(f"poche opzioni 1, {options}")
        return HttpResponseRedirect(reverse('polls:create-poll-2'))

    # remove white spaces before and at the end
    def trim_str(s: str) -> str:
        return s.strip()

    options = map(trim_str, options)
    # remove nulls
    options = list(filter(None, options))
    
    if len(options)<2:
        # todo: render error: add at least n-options
        # return HttpResponse(f"poche opzioni 2, {options}")
        return HttpResponseRedirect(reverse('polls:create-poll-2'))

    if len(options)>10:
        # todo: render error: not more than n-options
        # return HttpResponse("troppe opzioni")
        return HttpResponseRedirect(reverse('polls:create-poll-2'))

    # todo: check for duplicates

    # salva opzioni
    for option in options:
        PollOptionModel(value=option, poll_fk_id=poll_id).save()
    
    # return HttpResponse(str(options))
    
    return HttpResponseRedirect("%s?page=1&per_page=10" % reverse('polls:all_polls'))

