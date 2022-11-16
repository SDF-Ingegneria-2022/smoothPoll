from django.db import models
from polls.constants.models_constants import POLL_OPTION_MODEL_NAME


class VoteModel(models.Model):

    datetime: models.DateTimeField = models.DateTimeField(auto_now=True)
    poll_option: models.ForeignKey = models.ForeignKey(POLL_OPTION_MODEL_NAME, on_delete=models.CASCADE)

    def __str__(self):
        return str({
            'id': self.id,
            'datetime': self.datetime, 
            'poll_option': str(self.poll_option)
        })

