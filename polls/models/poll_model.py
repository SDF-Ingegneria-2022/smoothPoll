from typing import List
from django.db import models
from django.db.models import CharField
from polls.models.poll_option_model import PollOptionModel


class PollModel(models.Model): 


    name: CharField = models.CharField(max_length=200)
    question: CharField = models.CharField(max_length=200)
    poll_type: CharField = models.CharField(max_length=200, default="single_option")

    def __str__(self):
        return str({
            'id': self.id, 
            'name': self.name,
            'question': self.question
        })

    def options(self) -> List[PollOptionModel]:
        return list(PollOptionModel.objects.filter(poll_fk=self.id))         
        