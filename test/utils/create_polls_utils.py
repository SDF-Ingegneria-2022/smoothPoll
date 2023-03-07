from typing import List
import random
import string
from apps.polls_management.classes.poll_form_utils.poll_form import PollForm
from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.services.poll_create_service import PollCreateService


def create_single_option_poll(user, 
                name: str = "Form name", 
                question: str = "Form question?",
                votable_mj: bool = True,
                short_id: str = ''.join(random.choice(string.ascii_lowercase) for i in range(6))
                ) -> PollModel:
    
    single_option_form: PollForm = PollForm({
                                            "name": name, 
                                            "question": question, 
                                            "poll_type": "single_option", 
                                            "votable_mj": votable_mj, 
                                            "short_id": short_id
                                            })
    
    single_option_options: List[str] = ["Option 1", "Option 2", "Option 3"]
    
    # User creation
    user = user.objects.create_user(username="user", password="password")
    
    poll: PollModel = PollCreateService.create_or_edit_poll(single_option_form, single_option_options,user=user)
        
    return poll
    