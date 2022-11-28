from django.db import models
from django.db.models import CharField
from ..constants.models_constants import POLL_MODEL_NAME

class PollOptionModel(models.Model): 
    # key: CharField = models.CharField(max_length=200)
    value: CharField = models.CharField(max_length=200)
    poll_fk: models.ForeignKey = models.ForeignKey(POLL_MODEL_NAME, on_delete=models.CASCADE)

    def __str__(self):
        return str({
            'id': self.id, 
            # 'key': self.key,
            'value': self.value, 
            'poll': str(self.poll_fk)
        })
