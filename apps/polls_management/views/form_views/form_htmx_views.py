from apps.polls_management.classes.poll_form_utils.poll_form_session import SESSION_FORMDATA, SESSION_OPTIONS, get_poll_form
from apps.polls_management.exceptions.poll_not_valid_creation_exception import *
from django.views.decorators.http import require_http_methods
from django.http import HttpRequest, HttpResponse, Http404
from django.shortcuts import render

from allauth.account.decorators import login_required

@require_http_methods(["POST"])
@login_required
def poll_form_htmx_edit(request: HttpRequest):
    """
    Edit poll form through data sent by HTMX request. 
    Output is nothing.
    """
    if not request.htmx:
        raise Http404()

    # update main form data with what has been 
    # passed through POST (then save it in session)
    poll_form = get_poll_form(request)
    request.session[SESSION_FORMDATA] = poll_form.data

    return HttpResponse()


@require_http_methods(["POST"])
@login_required
def poll_form_htmx_create_option(request: HttpRequest):
    """
    Create an option when called from an HTMX request. 
    Output is HTML fragment of new option.
    """
    if not request.htmx:
        raise Http404()

    options = request.session.get(SESSION_OPTIONS) or {}

    # find the first free option index
    i = 1
    while i<=10 and str(i) in options:
        i += 1

    # Check I have space for a further option
    if i==11:
        # return a warning message (that will disappear in some seconds)
        return render(request, "polls_management/components/htmx_snack_warning.html", {
            "message": "Attenzione, non è possibile creare più di 10 opzioni."
        })
    
    # write in that index the option
    options[str(i)] = ""

    # SAVE CHANGES in session
    request.session[SESSION_OPTIONS] = options

    # return new option input 
    return render(request, 'polls_management/components/htmx_option_input.html', {
        "option": "", 
        'i': i, 
    })


@require_http_methods(["POST"])
@login_required
def poll_form_htmx_edit_option(request: HttpRequest, option_rel_id: int):
    """
    Change value of a certain option (while use type into).
    It is called by an HTMX request. Output is none.
    """
    if not request.htmx:
        raise Http404()

    # edit choosen option value and save in session
    options = request.session.get(SESSION_OPTIONS) or {}
    options[str(option_rel_id)] = request.POST[f"option-{option_rel_id}"]
    request.session[SESSION_OPTIONS] = options

    return HttpResponse()


@require_http_methods(["DELETE"])
@login_required 
def poll_form_htmx_delete_option(request: HttpRequest, option_rel_id: int):
    """
    Delete an option when called from an HTMX request. 
    Output is HTML fragment of new option.
    """
    if not request.htmx:
        raise Http404() 

    # remove choosen option and save in session

    options = request.session.get(SESSION_OPTIONS) or {}
    options.pop(str(option_rel_id), None)
    request.session[SESSION_OPTIONS] = options

    return HttpResponse()