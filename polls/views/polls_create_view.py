from polls.classes.poll_form import PollForm
from polls.models.poll_option_model import PollOptionModel
from django.http import HttpRequest, HttpResponseRedirect, HttpResponse
from django.contrib.sessions.backends.base import SessionBase
from django.shortcuts import render
from django.urls import reverse
from django.views import View


def create_poll_start(request: HttpRequest):
    return HttpResponseRedirect(reverse('polls:create-poll-1'))

def clean_session_key(session: SessionBase, keyname: str):
    if session.get(keyname) is not None:
        del session[keyname]

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

        form = PollForm(request.session.get('create-poll-s1-form-data') or None)
        return render(request, "polls/create_poll_step_1.html", {
            "form": form, 
            'enable_save': request.session.get('create-poll-enable-save'), 
            'error': request.session.get('create-poll-s1-error'), 
        })

    def post(self, request: HttpRequest, *args, **kwargs):
        """
        Post request should take passed input as a form, 
        validate it, and eventually redirect to next step
        """
        
        form = PollForm(request.POST or None)
        request.session['create-poll-s1-form-data'] = request.POST or None

        if not form.is_valid():
            # disable save
            request.session['create-poll-enable-save'] = False

            # display error w. session + redirect
            request.session['create-poll-s1-error'] = "Compila tutti i campi prima di proseguire"
            return HttpResponseRedirect(reverse('polls:create-poll-1'))

        # request.session['create-poll-s1-form-data'] = request.POST
        if request.session.get('create-poll-s1-error'):
            del request.session['create-poll-s1-error']

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
        if request.session.get("create-poll-s1-form-data") is None:
            # disable save
            request.session['create-poll-enable-save'] = False

            # display error w. session + redirect
            request.session['create-poll-s1-error'] = "Compila tutti i campi prima di proseguire"
            return HttpResponseRedirect(reverse('polls:create-poll'))

        return render(request, "polls/create_poll_step_2.html", {
            'options': request.session.get('create-poll-s2-options'), 
            'error': request.session.get('create-poll-s2-error'), 
            'enable_save': request.session.get('create-poll-enable-save'), 
        })

    def post(self, request: HttpRequest, *args, **kwargs):
        """
        Post request should handle and validate options.

        If they are all OK, it confirms poll creation 
        and apply changes in DB
        """

        # redirect if prec. steps are not done
        if request.session.get("create-poll-s1-form-data") is None:
            # disable save
            request.session['create-poll-enable-save'] = False

            # display error w. session + redirect
            request.session['create-poll-s1-error'] = "Compila tutti i campi prima di proseguire"
            return HttpResponseRedirect(reverse('polls:create-poll'))

        options = request.POST.getlist("options[]")
    
        if options is None:
            # disable save
            request.session['create-poll-enable-save'] = False

            # display error w. session + redirect
            request.session['create-poll-s2-error'] = "Inserisci almeno 2 opzioni"
            return HttpResponseRedirect(reverse('polls:create-poll-2'))

        # remove white spaces before and at the end
        def trim_str(s: str) -> str:
            return s.strip()
        options = map(trim_str, options)

        # remove nulls
        options = list(filter(None, options))

        request.session['create-poll-s2-options'] = options
        
        if len(options)<2:
            # disable save
            request.session['create-poll-enable-save'] = False

            # display error w. session + redirect
            request.session['create-poll-s2-error'] = "Inserisci almeno 2 opzioni"
            return HttpResponseRedirect(reverse('polls:create-poll-2'))

        if len(options)>10: 
            # disable save
            request.session['create-poll-enable-save'] = False

            # display error w. session + redirect
            request.session['create-poll-s2-error'] = "Errore, non puoi inserire più di 10 opzioni"
            return HttpResponseRedirect(reverse('polls:create-poll-2'))

        # todo: check for duplicates

        # remove eventual errors
        if request.session.get('create-poll-s2-error') is not None:
            del request.session['create-poll-s2-error']

        # enable save
        request.session['create-poll-enable-save'] = True

        return HttpResponseRedirect(reverse('polls:create-poll-2'))


def create_poll_confirm(request: HttpRequest):
    """
    Confirm creation and apply changes (creating objects and saving them in DB)
    """

    form = PollForm(request.session.get('create-poll-s1-form-data'))
    options = request.session.get('create-poll-s2-options')

    # todo: repeat validation

    # save poll 
    poll = form.save()
        
    # save options
    for option in options:
        PollOptionModel(value=option, poll_fk=poll).save()

    # clear session
    # request.session.delete('create-poll-s1-form-data')
    # request.session.delete('create-poll-s2-options')
    # request.session.delete('create-poll-s1-error')
    # request.session.delete('create-poll-s2-error')
    # request.session.delete('create-poll-enable-save')

    del request.session['create-poll-s1-form-data']
    del request.session['create-poll-s2-options']
    if request.session.get('create-poll-s1-error') is not None:
        del request.session['create-poll-s1-error']
    if request.session.get('create-poll-s2-error') is not None:
        del request.session['create-poll-s2-error']
    if request.session.get('create-poll-enable-save') is not None:
        del request.session['create-poll-enable-save']

    return HttpResponseRedirect("%s?page=last&per_page=10" % reverse('polls:all_polls'))        

