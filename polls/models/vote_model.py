from django.db import models
from django.db.models import DateTimeField, ForeignKey

from ..constants.models_constants import VOTE_MODEL_NAME


class VoteModel(models.Model):

    datetime: DateTimeField = models.DateTimeField(_(""), auto_now=True, auto_now_add=True)
    poll_option_fk: ForeignKey = models.ForeignKey(VOTE_MODEL_NAME, on_delete=models.CASCADE)