from polls.classes.poll_form import PollForm, PollOptionForm

from django.views.decorators.http import require_http_methods
from django.http import HttpRequest, HttpResponseRedirect, HttpResponse, Http404, HttpResponseNotModified
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.forms import formset_factory



SESSION_FORMDATA = 'create-poll-form'
SESSION_OPTIONS = 'create-poll-options'
SESSION_DATA = [SESSION_FORMDATA, SESSION_OPTIONS]

PollOptionFormset = formset_factory(PollOptionForm, extra=0)
PollOptionFormsetNew = formset_factory(PollOptionForm, extra=1)


class CreatePollHtmxView(View):
    """
    Render page w form to create a new poll. 

    Form has a regular part (handled normally through POST) and 
    an htmx part (to handle options).
    """
    
    def get(self, request: HttpRequest, *args, **kwargs):
        """
        Get request should render a form which allows user to fill it
        with poll's basic data 
        """

        # request.session.clear()

        form = PollForm(request.session.get(SESSION_FORMDATA) or None)
        options: dict = request.session.get(SESSION_OPTIONS) or {
            "1":"opzione 1", 
            "2":"opzione 2", 
        }

        request.session[SESSION_FORMDATA] = form.data
        request.session[SESSION_OPTIONS] = options

        return render(request, "polls/create_poll_htmx.html", {
            "poll_form": form, "options": options, 
            "error": request.session.get('create-poll-s1-error'), 
        })

    def post(self, request: HttpRequest, *args, **kwargs):
        """
        Post request should take passed input as a form, 
        validate it, and eventually redirect to next step
        """

        # retrieve data from session
        form = PollForm(request.session.get(SESSION_FORMDATA) or None)
        options = PollOptionFormset(initial=request.session.get(SESSION_OPTIONS) or [])

        # validate data
        # todo: ... 

        # perform object creation
        # todo: ...

        # clean session 
        for key in SESSION_OPTIONS:
            if request.session.get(key) is not None:
                del request.session[key]
      
        return HttpResponseRedirect("%s?page=last&per_page=10" % reverse('polls:all_polls'))        


        
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
        return HttpResponseNotModified()
        # render(request, "polls/components/htmx_snack_error.html", {
        #     "message": "Errore, non è possibile aggiungere più di 10 opzioni"
        # })
    
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