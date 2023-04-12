
from django.db import models
from django.conf import settings
from django.db.models import CharField
from sesame.utils import get_query_string

from apps.polls_management.constants.models_constants import POLL_MODEL_NAME

class PollTokens(models.Model):

    """Class used to represent a database table containing poll specific tokens and validation flags."""

    poll_fk: models.ForeignKey = models.ForeignKey(POLL_MODEL_NAME, on_delete=models.CASCADE)

    token_user: models.ForeignKey = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        default=None, blank=True, null=True,
    )

    single_option_use: models.BooleanField = models.BooleanField(default=False)

    majority_use: models.BooleanField = models.BooleanField(default=False)

    def __str__(self):
        return str({
            'id': self.id,
            'poll': str(self.poll_fk),
            'user': self.token_user.username,
            'single_use': self.single_option_use,
            'majority_use': self.majority_use
        })
    
    def get_token_url(self, host: str) -> str:
        """Return the link that voter may use to vote with this token."""
        link: str = host + '/' + self.poll_fk.short_id
        link += get_query_string(user=self.token_user, scope=f"Poll:{self.poll_fk.id}")
        return link