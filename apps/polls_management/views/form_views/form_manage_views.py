from typing import List
from apps.polls_management.classes.poll_form_utils.poll_form_session import SESSION_ERROR, SESSION_FORMDATA, SESSION_IS_EDIT, SESSION_OPTIONS, SESSION_POLL_ID, clean_session, get_poll_form
from apps.polls_management.exceptions.poll_does_not_exist_exception import PollDoesNotExistException
from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.services.poll_create_service import PollCreateService
from apps.polls_management.exceptions.poll_not_valid_creation_exception import *
from apps.polls_management.services.poll_service import PollService
from django.http import HttpRequest, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from allauth.account.decorators import login_required

from apps.polls_management.services.poll_token_service import PollTokenService


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

        # temporary override of options 
        try:
            options = get_poll_options_from_post(request)
        except:
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
            # prepare message error to explain there are too few options
            request.session[SESSION_ERROR] = f"Attenzione, una scelta di tipo {form.get_type_verbose_name()} "
            
            if form.data.get("votable_mj", False) and form.data.get("poll_type")!=PollModel.PollType.MAJORITY_JUDJMENT: 
                # handle polls votable also w MJ
                request.session[SESSION_ERROR] += "(giudicabile anche con il Giudizio Maggioritario) "
            
            request.session[SESSION_ERROR] += f"richiede almeno {form.get_min_options()} opzioni. "
            
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
    
    if poll.is_votable_token():
        token_links = PollTokenService.available_token_list(poll)
        invalid_tokens = PollTokenService.unavailable_token_list(poll)
        
        return render(request, 'polls_management/confirm_form.html', {'poll': poll, 'edit': request.session.get(SESSION_IS_EDIT), 'token_list': token_links, 'invalid_tokens': invalid_tokens})
    else:
        return render(request, 'polls_management/confirm_form.html', {
            'poll': poll, 
            'edit': request.session.get(SESSION_IS_EDIT)
        })


def get_poll_options_from_post(request: HttpRequest):
    """TEMP method for extracting poll options from POST
    TODO: fix in a seriuous way"""

    options_keys = [k for k in request.POST.keys() if k.startswith("option-")]
    
    options = {}
    for k in options_keys:
        options[k.split("-")[1]] = request.POST.get(k)
    
    return options


    