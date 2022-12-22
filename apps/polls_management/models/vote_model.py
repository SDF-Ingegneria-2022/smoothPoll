from django.db import models
from apps.polls_management.models.poll_option_model import PollOptionModel
from apps.polls_management.models.poll_model import PollModel

class VoteModel(models.Model):
    """
    A Vote to a certain Poll. 
    It's the classic choice of an option.
    """

    datetime: models.DateTimeField = models.DateTimeField(auto_now=True)
    """Timestamp of vote registration instant"""

    poll_option: models.ForeignKey = models.ForeignKey(PollOptionModel, on_delete=models.CASCADE)
    """choosed poll option"""

    def poll(self) -> PollModel: 
        """
        Retrieve corresponding Poll of this Vote.
        """
        option: PollOptionModel = self.poll_option
        return option.poll_fk

    def __str__(self):
        return str({
            'id': self.id,
            'datetime': self.datetime, 
            'poll_option': str(self.poll_option)
        })
