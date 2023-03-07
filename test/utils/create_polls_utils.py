from typing import List
import random
import string
from apps.polls_management.classes.poll_form_utils.poll_form import PollForm
from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.services.poll_create_service import PollCreateService


def create_single_option_polls(
                django_user_model, 
                number_of_polls: int = 3,
                name: str = "Form name", 
                question: str = "Form question?",
                votable_mj: bool = True,
                ) -> List[PollModel]:
    """Create single option polls. Due to the ownrship of the poll, the 'django_user_model' must be injected before.

    Args:
        django_user_model (Any): Django user model. Used to create the user that will own the poll.
        number_of_polls (int, optional): Number of polls to create. Defaults to 3.
        name (str, optional): Poll name. Defaults to "Form name".
        question (str, optional): Poll question. Defaults to "Form question?".
        votable_mj (bool, optional): If true the single option poll can be voted also with the mj criteria. Defaults to True.

    Returns:
        PollModel: Poll created.
    """
    # User creation
    user = django_user_model.objects.create_user(username="user", password="password")
    polls_created: List[PollModel] = []
    
    for index in range(number_of_polls): 
        single_option_form: PollForm = PollForm({
                                                "name": name + f" {str(index)}", 
                                                "question": question + f" {str(index)}", 
                                                "poll_type": "single_option", 
                                                "votable_mj": votable_mj, 
                                                "short_id": ''.join(random.choice(string.ascii_lowercase) for i in range(6))
                                                })
        
        single_option_options: List[str] = ["Option 1", "Option 2", "Option 3"]
        
        polls_created.append(PollCreateService.create_or_edit_poll(single_option_form, single_option_options,user=user))
        
    return polls_created
    