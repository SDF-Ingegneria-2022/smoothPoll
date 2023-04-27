from apps.polls_management.models.poll_model import PollModel


def nonauth_user_template_name(poll: PollModel) -> str:
    """Name of template to display if user is not 
    authorized to perform a vote"""

    if poll.is_votable_google():
        return 'global/login.html'
    
    return 'polls_management/token_poll_redirect.html'