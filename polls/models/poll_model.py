from polls.models.poll_option_model import PollOptionModel

from typing import List
from django.db import models
from django.db.models import CharField
from django.utils.translation import gettext as _


class PollModel(models.Model): 

    class PollType(models.TextChoices):
        """Possible vode modes a PollModel can 
        be voted. In this system, each PollModel 
        belongs to one PollType"""
        SINGLE_OPTION = 'single_option', _('Opzione Singola')
        MAJORITY_JUDJMENT = 'majority_judjment', _('Giudizio Maggioritario')

    name: CharField = models.CharField(
        max_length=200, verbose_name=_('Nome Sondaggio'))

    question: CharField = models.CharField(
        max_length=200, verbose_name=_("Quesito"))

    poll_type: CharField = models.CharField(
        max_length=200,
        choices=PollType.choices, 
        default=PollType.SINGLE_OPTION)

    def __str__(self):
        return str({
            'id': self.id, 
            'name': self.name,
            'question': self.question,
            'poll_type': self.poll_type, 
        })

    def options(self) -> List[PollOptionModel]:
        return list(PollOptionModel.objects.filter(poll_fk=self.id))         
        