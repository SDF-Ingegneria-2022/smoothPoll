from ..constants.models_constants import POLL_MODEL_NAME
from django.db import models

class MajorityVoteModel(models.Model):
    """Class representing the vote to a majority vote poll"""

    datetime: models.DateTimeField = models.DateTimeField(auto_now=True)
    """Timestamp of vote registration instant"""

    poll: models.ForeignKey = models.ForeignKey(POLL_MODEL_NAME, on_delete=models.CASCADE)
    """Reference to poll"""

    def __str__(self):
        return str({
            'id': self.id,
            'datetime': self.datetime, 
            'poll': str(self.poll)
        })