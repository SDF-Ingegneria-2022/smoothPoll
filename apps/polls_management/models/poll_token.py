
from django.utils import timezone
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

    created_at = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return self.get_token()
    
    def get_token_path(self) -> str:
        """Return the link that voter may use to vote with this token.
        example: '/pollshortid?token=abcdef1234qwerty'
        """
        return "/" + self.poll_fk.short_id + \
            get_query_string(user=self.token_user, scope=f"Poll:{self.poll_fk.id}")

    def get_token_query_string(self) -> str:
        """Return the query string that voter may use to vote with this token.
        example: '?token=abcdef1234qwerty'
        """
        return get_query_string(user=self.token_user, scope=f"Poll:{self.poll_fk.id}")
    
    def get_token(self) -> str:
        """Return the token that voter may use to vote with this token.
        example: 'abcdef1234qwerty'
        """
        return self.get_token_query_string().split('=')[1]