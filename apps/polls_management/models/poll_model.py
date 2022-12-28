import datetime
from apps.polls_management.models.poll_option_model import PollOptionModel

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

    open_datetime: models.DateTimeField = models.DateTimeField(
        default=None, blank=True, null=True, 
        verbose_name=_("Data Apertura")
    )

    def __str__(self):
        return str({
            'id': self.id, 
            'name': self.name,
            'question': self.question,
            'poll_type': self.poll_type, 
            'open_datetime': self.open_datetime, 
        })

    def is_open(self) -> bool:
        """Check if Poll is open"""
        
        # without timezone info
        if self.open_datetime is not None:
            return datetime.datetime.now().replace(tzinfo=None) > self.open_datetime.replace(tzinfo=None)
        else:
            return True

    def options(self) -> List[PollOptionModel]:
        return list(PollOptionModel.objects.filter(poll_fk=self.id))

    def get_type_verbose_name(self) -> str:

        if self.poll_type == PollModel.PollType.MAJORITY_JUDJMENT:
            return "Giudizio Maggioritario"
        elif self.poll_type == PollModel.PollType.SINGLE_OPTION:
            return "Opzione Singola"

        return "Nessun Tipo"

    def get_type_color(self) -> str:

        if self.poll_type == PollModel.PollType.MAJORITY_JUDJMENT:
            return "#253495"
        elif self.poll_type == PollModel.PollType.SINGLE_OPTION:
            return "#F6AA1C"

        return "#363732"