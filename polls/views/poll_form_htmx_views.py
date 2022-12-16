from polls.classes.poll_form import PollForm # , PollOptionForm
from polls.services.poll_create_service import PollCreateService
from polls.exceptions.poll_not_valid_creation_exception import *

from django.views.decorators.http import require_http_methods
from django.http import HttpRequest, HttpResponseRedirect, HttpResponse, Http404, HttpResponseNotModified
from django.shortcuts import render
from django.urls import reverse
from django.views import View

SESSION_FORMDATA = 'create-poll-form'
SESSION_OPTIONS = 'create-poll-options'
SESSION_ERROR = 'create-poll-error'
_ALL_SESSION_KEYS = [SESSION_FORMDATA, SESSION_OPTIONS, SESSION_ERROR]


class CreatePollHtmxView(View):
    """
    Render page w form to create a new poll. 

    Form has a regular part (handled normally through POST) and 
    an htmx part (to handle options).
    """
    
    def get(self, request: HttpRequest, *args, **kwargs):
        """
        Get request should render a form which allows user to fill:
        - main data form (to enter name and question)
        - options form (to dynamically add, remove and edit options)

        Eventual data in session will be displayed.

        Occasionally, there may even be rendered errors.
        """

        # request.session.clear()

        # get data from session or init it 
        form = PollForm(request.session.get(SESSION_FORMDATA) or None)
        options: dict = request.session.get(SESSION_OPTIONS) or {
            "1":"", 
            "2":"", 
        }

        request.session[SESSION_FORMDATA] = form.data
        request.session[SESSION_OPTIONS] = options

        return render(request, "polls/create_poll_htmx.html", {
            "poll_form": form, "options": options, 
            "error": request.session.get(SESSION_ERROR), 
        })

    def post(self, request: HttpRequest, *args, **kwargs):
        """
        This post request has purpose of saving all poll 
        data kept in session. It doesn't really receive 
        any data from user, it just:
        - take a confim
        - get all data from session
        - validate it
        - perform save/creation of Poll and related Options
        - clean session

        In case of (validation) errors, it saves them in session
        and redirect to GET so they may be displayed
        """

        # retrieve data from session
        form = PollForm(request.session.get(SESSION_FORMDATA) or None)
        options = request.session.get(SESSION_OPTIONS) or {}

        try:
            # perform object creation
            PollCreateService.create_new_poll(form, options.values())
        except PollMainDataNotValidException:
            request.session[SESSION_ERROR] = "Attenzione, un sondaggio ha bisogno di un nome e di una domanda validi"
            return HttpResponseRedirect(reverse('polls:create_poll_form'))
        except TooFewOptionsException:
            request.session[SESSION_ERROR] = "Attenzione, un sondaggio ha bisogno almeno 2 opzioni"
            return HttpResponseRedirect(reverse('polls:create_poll_form'))
        except TooManyOptionsException:
            request.session[SESSION_ERROR] = "Attenzione, un sondaggio può avere al massimo 10 optioni"
            return HttpResponseRedirect(reverse('polls:create_poll_form'))

        # clean session 
        for key in _ALL_SESSION_KEYS:
            if request.session.get(key) is not None:
                del request.session[key]
      
        return HttpResponseRedirect("%s?page=last&per_page=10" % reverse('polls:all_polls'))        


def poll_form_clean_go_back_home(request: HttpRequest):
    """Clean session and go back home"""

    # clean session 
    for key in _ALL_SESSION_KEYS:
        if request.session.get(key) is not None:
            del request.session[key]

    return HttpResponseRedirect("%s?page=1&per_page=10" % reverse('polls:all_polls'))        

        
@require_http_methods(["POST"])
def poll_form_htmx_edit(request: HttpRequest):
    """
    Edit poll form through data sent by HTMX request. 
    Output is nothing.
    """
    if not request.htmx:
        raise Http404()

    poll_form = PollForm(request.POST or None)
    request.session[SESSION_FORMDATA] = poll_form.data

    print(request.session[SESSION_FORMDATA])

    return HttpResponse()


@require_http_methods(["POST"])
def poll_form_htmx_create_option(request: HttpRequest):
    """
    Create an option when called from an HTMX request. 
    Output is HTML fragment of new option.
    """
    if not request.htmx:
        raise Http404()

    options = request.session.get(SESSION_OPTIONS) or {}

    # find first free option index
    i = 1
    while i<=10 and str(i) in options:
        i += 1

    if i==11:
        # todo: raise error
        print(request.session[SESSION_OPTIONS])
        # return HttpResponseNotModified()
        return render(request, "polls/components/htmx_snack_warning.html", {
            "message": "Attenzione, non è possibile creare più di 10 opzioni."
        })
    
    # write in that index the option
    options[str(i)] = ""

    # SAVE CHANGES
    request.session[SESSION_OPTIONS] = options

    print(request.session[SESSION_OPTIONS])

    return render(request, 'polls/components/htmx_option_input.html', {
        "option": "", 
        'i': i, 
    })


@require_http_methods(["POST"])
def poll_form_htmx_edit_option(request: HttpRequest, option_rel_id: int):
    """
    Change value of a certain option (while use type into).
    It is called by an HTMX request. Output is none.
    """
    if not request.htmx:
        raise Http404()

    options = request.session.get(SESSION_OPTIONS)

    options[str(option_rel_id)] = request.POST[f"option-{option_rel_id}"]

    request.session[SESSION_OPTIONS] = options

    print(request.session[SESSION_OPTIONS])

    return HttpResponse()


@require_http_methods(["DELETE"])
def poll_form_htmx_delete_option(request: HttpRequest, option_rel_id: int):
    """
    Delete an option when called from an HTMX request. 
    Output is HTML fragment of new option.
    """
    if not request.htmx:
        raise Http404()

    options = request.session.get(SESSION_OPTIONS)

    options.pop(str(option_rel_id), None)

    request.session[SESSION_OPTIONS] = options

    print(request.session[SESSION_OPTIONS])

    return HttpResponse()