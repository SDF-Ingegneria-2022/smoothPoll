import abc
from typing import List
import pytest

from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.models.poll_option_model import PollOptionModel
from apps.polls_management.models.schulze_vote_model import SchulzeVoteModel
from apps.votes_results.classes.schulze_results.schulze_results_adapter import SchulzeResultsAdapter


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

            'poll_case_1': self.generate_poll(
                name="Dummy3", question="Dummy question3?",
                options=["A", "B", "C", "D", ],
                author=user3, ), 

            'poll_case_23': self.generate_poll(
                name="Dummy4", question="Dummy question4?",
                options=["A", "B", "C", "D", "E"],
                author=user4, ),  
            }

    def generate_votes(self, schulze_poll, user_inputs: List[int]):

        schulze: SchulzeVoteModel = SchulzeVoteModel(poll=schulze_poll)
        schulze.set_order(user_inputs)
        schulze.save()

    def generate_votes_in_bulk(self, schulze_poll, input: List[int], num_votes: int):

        while num_votes>0:
            self.generate_votes(schulze_poll, input)
            num_votes -= 1

    @pytest.fixture()
    def test_votes1(self, test_polls):

        poll_test: PollModel = test_polls['poll_case_23']

        op4 = poll_test.options()[4].id #E
        op3 = poll_test.options()[3].id #D
        op2 = poll_test.options()[2].id #C
        op1 = poll_test.options()[1].id #B
        op0 = poll_test.options()[0].id #A

        # 5 people think A > C > B > E > D.
        input_user1: List[int] = [op0, op2, op1, op4, op3]
        # 5 people think A > D > E > C > B.
        input_user2: List[int] = [op0, op3, op4, op2, op1]
        # 8 people think B > E > D > A > C.
        input_user3: List[int] = [op1, op4, op3, op0, op2]
        # 3 people think C > A > B > E > D.
        input_user4: List[int] = [op2, op0, op1, op4, op3]
        # 7 people think C > A > E > B > D.
        input_user5: List[int] = [op2, op0, op4, op1, op3]
        # 2 people think C > B > A > D > E.
        input_user6: List[int] = [op2, op1, op0, op3, op4]
        # 7 people think D > C > E > B > A.
        input_user7: List[int] = [op3, op2, op4, op1, op0]
        # 8 people think E > B > A > D > C.
        input_user8: List[int] = [op4, op1, op0, op3, op2]

        votes1: int = 5
        votes2: int = 5
        votes3: int = 8
        votes4: int = 3
        votes5: int = 7
        votes6: int = 2
        votes7: int = 7
        votes8: int = 8

        self.generate_votes_in_bulk(poll_test, input_user1, votes1)
        self.generate_votes_in_bulk(poll_test, input_user2, votes2)
        self.generate_votes_in_bulk(poll_test, input_user3, votes3)
        self.generate_votes_in_bulk(poll_test, input_user4, votes4)
        self.generate_votes_in_bulk(poll_test, input_user5, votes5)
        self.generate_votes_in_bulk(poll_test, input_user6, votes6)
        self.generate_votes_in_bulk(poll_test, input_user7, votes7)
        self.generate_votes_in_bulk(poll_test, input_user8, votes8)

        # Expected results:  E > A > C > B > D

        return {'case1': poll_test}