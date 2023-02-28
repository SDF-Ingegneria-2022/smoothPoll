from apps.polls_management.classes.poll_form import PollForm
from apps.polls_management.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
from apps.polls_management.models.majority_vote_model import MajorityVoteModel
from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.models.poll_option_model import PollOptionModel
from apps.polls_management.models.vote_model import VoteModel
from apps.polls_management.services.poll_create_service import PollCreateService
from apps.polls_management.exceptions.poll_not_valid_creation_exception import *
from apps.polls_management.services.poll_service import PollService

from django.views.decorators.http import require_http_methods
from django.http import HttpRequest, HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from allauth.account.decorators import login_required

# -------------------------------------------------
# Session keys used to store form data 
# (or create/edit process data)

SESSION_FORMDATA = 'create-poll-form'
SESSION_POLL_ID = 'poll-instance'
SESSION_OPTIONS = 'create-poll-options'
SESSION_ERROR = 'create-poll-error'
SESSION_IS_EDIT = 'is-edit'


_ALL_SESSION_KEYS = [
    SESSION_FORMDATA, 
    SESSION_OPTIONS, 
    SESSION_ERROR, 
    SESSION_POLL_ID, 
    SESSION_IS_EDIT ]

# -------------------------------------------------
# Session util methods (methods to perform some
# operations on session during creation)

def clean_session(request: HttpRequest) -> None: 
    """Clean current session from form data"""

    # iterate all keys used to store form data
    # to delete each of them
    for key in _ALL_SESSION_KEYS:
        if request.session.get(key) is not None:
            del request.session[key]


def get_poll_form(request: HttpRequest) -> PollForm:
    """Factory method to get current form 
    from session (or from POST request)."""

    # build a form for creation (w most updated data)
    if request.session.get(SESSION_POLL_ID) is None:
        return PollForm(request.POST or request.session.get(SESSION_FORMDATA) or None)

    # build a form for editing an existing instance
    try:
        return PollForm(
            # fill form data w current most updated
            request.POST or request.session.get(SESSION_FORMDATA) or None, 

            # connect form to existing instance
            instance=PollService.get_poll_by_id(
                request.session.get(SESSION_POLL_ID))
        )
    except PollDoesNotExistException:
        raise Http404(f"Poll with id {request.session.get(SESSION_POLL_ID)} not found.")


# -------------------------------------------------
# Init views: views used to init the creation 
# or edit processes

@login_required
def create_poll_init_view(request: HttpRequest):
    """View to inizialize form for new poll creation"""

    # clean session from eventual mess
    clean_session(request)

    # poll and option will be inited creating new ones
    # (because session is clean)
    
    # redirect to form to permit edit
    return HttpResponseRedirect(reverse('apps.polls_management:poll_form'))        

@login_required
def edit_poll_init_view(request: HttpRequest, poll_id: int):
    """View to inizialize form for new poll creation"""

    # clean session from eventual mess
    clean_session(request)
    
    try:
        # Retrieve poll
        poll: PollModel = PollService.get_poll_by_id(poll_id)
    except PollDoesNotExistException:
        raise Http404(f"Poll with id {poll_id} not found.")
    
    if (not request.user == poll.author):
        return render(request, 'global/not-author.html')

    # Check if poll is open and can be edit
    if poll.is_open() or poll.is_closed():
        request.session['cannot_edit'] = True
        return HttpResponseRedirect("%s?page=last&per_page=10" % reverse('apps.polls_management:all_user_polls'))

    # init form with poll instance that should be modified 
    form = PollForm({
        "name": poll.name, 
        "question": poll.question, 
        "poll_type": poll.poll_type, 
        "open_datetime": poll.open_datetime,
        "close_datetime": poll.close_datetime,  
        "autor": poll.author,
        "votable_mj": poll.votable_mj, 
    }, instance=poll)

    # init poll options with current ones
    options: dict = {}
    i: int = 1
    for o in poll.options():
        options[str(i)] = o.value
        i += 1

    # save everythingh in session, so form can be 
    # rendered with current data
    request.session[SESSION_FORMDATA] = form.data
    request.session[SESSION_POLL_ID] = poll.id
    request.session[SESSION_OPTIONS] = options

    request.session[SESSION_IS_EDIT] = True

    # redirect to form to permit edit
    return HttpResponseRedirect(reverse('apps.polls_management:poll_form'))   


# -------------------------------------------------
# Proper form views: views to handle the 
# create/edit form (both the htmx dynamic part and 
# the "final confirmation")


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

        # get from and option from session or init it 
        form = get_poll_form(request)

        options: dict = request.session.get(SESSION_OPTIONS) or {"1":"", "2":"", }

        # render form
        return render(request, "polls_management/create_poll_htmx.html", {
            "poll_form": form, "options": options, 
            "error": request.session.get(SESSION_ERROR), 
            "edit": request.session.get(SESSION_IS_EDIT)
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

        # retrieve data from session (or POST)
        form = get_poll_form(request)
        options = request.session.get(SESSION_OPTIONS) or {}
        current_user = request.user
        
        # create object or apply changes
        # (if an error occours, redirect to GET 
        # to re-render the form)
        try:
            poll = PollCreateService.create_or_edit_poll(form, options.values(), current_user)
            request.session[SESSION_POLL_ID] = poll.id
        except PollMainDataNotValidException:
            request.session[SESSION_ERROR] = "Attenzione, inserisci tutti i dati richiesti prima di procedere"
            return HttpResponseRedirect(reverse('apps.polls_management:poll_form'))
        except TooFewOptionsException:
            request.session[SESSION_ERROR] = f"Attenzione, una scelta di tipo {form.get_type_verbose_name()} ha bisogno almeno {form.get_min_options()} opzioni"
            return HttpResponseRedirect(reverse('apps.polls_management:poll_form'))
        except TooManyOptionsException:
            request.session[SESSION_ERROR] = "Attenzione, una scelta può avere al massimo 10 opzioni"
            return HttpResponseRedirect(reverse('apps.polls_management:poll_form'))

        # after changes are applied, redirect to confirm page
        # (+ add a parameter to track GA)
        if poll.poll_type == PollModel.PollType.MAJORITY_JUDJMENT:
            return HttpResponseRedirect(f"{reverse('apps.polls_management:poll_form_confirm_mj')}")        
        else:
            return HttpResponseRedirect(f"{reverse('apps.polls_management:poll_form_confirm_so')}")        

@login_required
def poll_form_clean_go_back_home(request: HttpRequest):
    """Clean session and go back home"""

    # clean session and get back to homepage
    clean_session(request)

    return HttpResponseRedirect(reverse('apps.polls_management:all_user_polls'))        

@login_required
def poll_form_confirm(request: HttpRequest): 
    """Confirm page that tells the user modifications have been applied"""

    poll_id = request.session.get(SESSION_POLL_ID, None)
    if poll_id is None:
        raise Http404()
    
    try:
        poll: PollModel = PollService.get_poll_by_id(poll_id)
    except PollDoesNotExistException:
        raise Http404(f"Poll with id {poll_id} not found.")
    

    return render(request, 'polls_management/confirm_form.html', {
        'poll': poll, 
        'edit': request.session.get(SESSION_IS_EDIT)
    })


        
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