from polls.classes.poll_form import PollForm
from polls.models.poll_option_model import PollOptionModel
from django.http import HttpRequest, HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views import View

def create_poll_start(request: HttpRequest):
    return HttpResponseRedirect(reverse('polls:create-poll-1'))

class CreatePollStep1View(View):
    """
    View which handles step 1 of creation of a new poll. It has
    responsability to let user type basic form data (like name 
    and question that should be asked)
    """
    
    def get(self, request: HttpRequest, *args, **kwargs):
        """
        Get request should render a form which allows user to fill it
        with poll's basic data
        """

        form = PollForm(None)
        return render(request, "polls/create_poll_step_1.html", {"form": form})

    def post(self, request: HttpRequest, *args, **kwargs):
        """
        Post request should take passed input as a form, 
        validate it, and eventually redirect to next step
        """
        
        form = PollForm(request.POST or None)

        if not form.is_valid():
            return HttpResponseRedirect(reverse('polls:create-poll-1'))

        poll = form.save()
        request.session['form-poll-id'] = poll.id

        return HttpResponseRedirect(reverse('polls:create-poll-2'))


class CreatePollStep2View(View):
    """
    View which handles step 2 of creation of a new poll. It has
    responsability to let user insert options, ensuring all 
    constraints are satisfied. 

    If user data is OK, it also performs the creation of 
    poll object.
    """

    def get(self, request: HttpRequest, *args, **kwargs):
        """
        Get request should render a form which allows user to 
        add and remove options.
        """

        # redirect if prec. steps are not done
        if request.session.get("form-poll-id") is None:
            return HttpResponseRedirect(reverse('polls:create-poll'))

        return render(request, "polls/create_poll_step_2.html", {
            'options': request.session.get('create-poll-s2-options'), 
            'error': request.session.get('create-poll-s2-error')
        })

    def post(self, request: HttpRequest, *args, **kwargs):
        """
        Post request should handle and validate options.

        If they are all OK, it confirms poll creation 
        and apply changes in DB
        """

        # redirect if prec. steps are not done
        if request.session.get("form-poll-id") is None:
            return HttpResponseRedirect(reverse('polls:create-poll'))

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

        # save options
        for option in options:
            PollOptionModel(value=option, poll_fk_id=request.session.get("form-poll-id")).save()
    
        return HttpResponseRedirect("%s?page=1&per_page=10" % reverse('polls:all_polls'))


    def perform_creation(self, form: PollForm, options: list[str]):

        # save poll 
        poll = form.save()
        
        # save options
        for option in options:
            PollOptionModel(value=option, poll_fk=poll).save()
