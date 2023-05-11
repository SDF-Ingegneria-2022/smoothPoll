import abc
from typing import List
import pytest

from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.models.poll_option_model import PollOptionModel


class HasTestPolls(abc.ABC):

    def generate_poll(self, name, question, options: List[str], author):

        poll = PollModel(name=name, question=question, author=author)
        poll.save()

        for option in options:
            poll_option = PollOptionModel(value=option, poll_fk=poll)
            poll_option.save()

        return poll
    

    @pytest.fixture()
    def test_polls(self, django_user_model):

        username = "user1"
        password = "bar"
        user = django_user_model.objects.create_user(username=username, password=password) 
        
        username2 = "user2"
        password2 = "bar"
        user2 = django_user_model.objects.create_user(username=username2, password=password2) 

        username3 = "user3"
        password3 = "bar"
        user3 = django_user_model.objects.create_user(username=username3, password=password3) 

        username4 = "user4"
        password4 = "bar"
        user4 = django_user_model.objects.create_user(username=username4, password=password4) 


        return {
            'voted_poll': self.generate_poll(
                name="Dummy", question="Dummy question?", 
                options=["Valore 1", "Valore 2", "Valore 3"], 
                author=user, ),

            'control_poll': self.generate_poll(
                name="Dummy2", question="Dummy question2?", 
                options=["Valore 1", "Valore 2", "Valore 3", "Valore 4"],
                author=user2, ), 

            'control_poll2': self.generate_poll(
                name="Dummy3", question="Dummy question3?",
                options=["A", "B", "C", "D", "E", "F"],
                author=user3, ), 

            'control_poll3': self.generate_poll(
                name="Dummy4", question="Dummy question4?",
                options=["A", "B", "C"],
                author=user4, ),  
            }
