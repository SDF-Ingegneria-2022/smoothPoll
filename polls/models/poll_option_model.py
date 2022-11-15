from django.db import models
from django.db.models import CharField

from polls.business.contants.models_constants import POLL_MODEL_NAME # type: ignore

class PollOptionModel(models.Model): 
    key: CharField = models.CharField(max_length=200)
    value: CharField = models.CharField(max_length=200)
    poll_fk: models.ForeignKey = models.ForeignKey(POLL_MODEL_NAME, on_delete=models.CASCADE)