from django.db import models
from polls.constants.models_constants import MAJORITY_VOTE_MODEL, POLL_OPTION_MODEL_NAME

class MajorityOption(models.Model):
    """Class which represents the majority vote choice and the
    rating for it"""
    
    rating: models.PositiveSmallIntegerField = models.PositiveSmallIntegerField(default=1)
    """Majority vote rating value"""

    poll_option: models.ForeignKey = models.ForeignKey(POLL_OPTION_MODEL_NAME, on_delete=models.CASCADE)
    """Choosed pool option"""

    #poll_majority_vote: models.ForeignKey = models.ForeignKey(MAJORITY_VOTE_MODEL, on_delete=models.CASCADE)
    #"""Choosed majority vote rating"""

    def __str__(self):
        return str({
            'id': self.id,
            'rating': str(self.rating), 
            'poll_option': str(self.poll_option)
            #'poll_majority_vote': str(self.poll_majority_vote)
        })
