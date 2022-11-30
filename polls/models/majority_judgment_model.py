from django.db import models
from polls.constants.models_constants import MAJORITY_VOTE_MODEL_NAME, POLL_OPTION_MODEL_NAME

class MajorityJudgmentModel(models.Model):
    """Class which represents a single rating voted on a
    majority poll"""
    
    rating: models.PositiveSmallIntegerField = models.PositiveSmallIntegerField(default=None)
    """Majority vote rating value"""

    poll_option: models.ForeignKey = models.ForeignKey(POLL_OPTION_MODEL_NAME, on_delete=models.CASCADE)
    """Choosed pool option"""

    majority_poll_vote: models.ForeignKey = models.ForeignKey(MAJORITY_VOTE_MODEL_NAME, null=True, on_delete=models.CASCADE)
    """Overall vote of a majority vote poll"""

    def __str__(self):
        return str({
            'id': self.id,
            'rating': str(self.rating), 
            'poll_option': str(self.poll_option)
        })
