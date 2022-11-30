from django.db import models
from polls.constants.models_constants import MAJORITY_VOTE_MODEL_NAME, POLL_OPTION_MODEL_NAME

class MajorityJudgmentModel(models.Model):
    """"""
    
    rating: models.PositiveSmallIntegerField = models.PositiveSmallIntegerField(default=None)
    """Majority vote rating value"""

    poll_option: models.ForeignKey = models.ForeignKey(POLL_OPTION_MODEL_NAME, on_delete=models.CASCADE)
    """Choosed pool option"""

    majority_poll_vote: models.ForeignKey = models.ForeignKey(MAJORITY_VOTE_MODEL_NAME, null=True, on_delete=models.CASCADE)
    """Rating of a majority poll option"""

    def __str__(self):
        return str({
            'id': self.id,
            'rating': str(self.rating), 
            'poll_option': str(self.poll_option)
        })
