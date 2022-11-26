from polls.models.majority_option import MajorityOption
from polls.models.poll_model import PollModel
from polls.models.poll_option_model import PollOptionModel
from ..constants.models_constants import MAJORITY_OPTION, POLL_MODEL_NAME
from django.db import models

class MajorityVoteModel(models.Model):
    """Class representing the vote to a majority vote poll"""

    datetime: models.DateTimeField = models.DateTimeField(auto_now=True)
    """Timestamp of vote registration instant"""

    poll: models.ForeignKey = models.ForeignKey(POLL_MODEL_NAME, on_delete=models.CASCADE)
    """Reference to poll"""

    rating_option: models.ForeignKey = models.ForeignKey(MAJORITY_OPTION, on_delete=models.CASCADE)
    """Reference to the single rating of a single option"""

    def poll_choosen(self) -> PollModel: 
        """
        Retrieve corresponding Poll of this Vote.
        """
        option: PollOptionModel = self.poll
        return option.poll_fk

    def rating_option_choosen(self) -> PollOptionModel:
        """
        Retrieve the majority option for this Vote
        """
        majority_option: MajorityOption = self.rating_option
        return majority_option.poll_option

    def __str__(self):
        return str({
            'id': self.id,
            'datetime': self.datetime, 
            'poll': str(self.poll),
            'poll_option': str(self.rating_option)
        })