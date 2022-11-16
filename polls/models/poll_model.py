from django.db import models
from django.db.models import CharField

class PollModel(models.Model): 
    name: CharField = models.CharField(max_length=200)
    question: CharField = models.CharField(max_length=200)

    def __str__(self):
        return str({
            'id': self.id, 
            'name': self.name,
            'question': self.question
        })