from ..constants.models_constants import MAJORITY_OPTION_MODEL_NAME, POLL_MODEL_NAME
from django.db import models

class MajorityVoteModel(models.Model):
    """Class representing the vote to a majority vote poll"""

    datetime: models.DateTimeField = models.DateTimeField(auto_now=True)
    """Timestamp of vote registration instant"""

    poll: models.ForeignKey = models.ForeignKey(POLL_MODEL_NAME, on_delete=models.CASCADE)
    """Reference to poll"""

    majority_poll_vote: models.ForeignKey = models.ForeignKey(MAJORITY_OPTION_MODEL_NAME, null=True, on_delete=models.CASCADE)
    """Rating of a majority poll option"""

    def __str__(self):
        return str({
            'id': self.id,
            'datetime': self.datetime, 
            'poll': str(self.poll)
        })