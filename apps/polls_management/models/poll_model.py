import datetime
from apps.polls_management.models.poll_option_model import PollOptionModel

from typing import List
from django.db import models
from django.db.models import CharField
from django.utils.translation import gettext as _
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model


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

    close_datetime: models.DateTimeField = models.DateTimeField(
        default=None, blank=True, null=True,
        verbose_name=_("Data Chiusura")
    )
    
    predefined: models.BooleanField = models.BooleanField(
        default=False, verbose_name=_("Predefinito")
    )

    votable_mj: models.BooleanField = models.BooleanField(
        default=False, verbose_name=_("Votabile con Giudizio Maggioritario")
    )

    author: models.ForeignKey = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE,
        default=1
    )

    def __str__(self):
        return str({
            'id': self.id, 
            'name': self.name,
            'question': self.question,
            'poll_type': self.poll_type, 
            'open_datetime': self.open_datetime, 
            'close_datetime': self.close_datetime,
            'predefined': self.predefined,
            'author': self.author,
        })

    def options(self) -> List[PollOptionModel]:
        return list(PollOptionModel.objects.filter(poll_fk=self.id))


    def is_open(self) -> bool:
        """Check if Poll is open"""

        if self.open_datetime is None:
            return False

        return timezone.now() > self.open_datetime

    def is_closed(self) -> bool:
        """Chech if Poll is closed"""
        
        if self.close_datetime is None:
            return False
        
        return timezone.now() > self.close_datetime

    def get_state_label(self) -> str: 
        """Get a label rappresentative of the state"""

        if self.is_closed():
            return "CHIUSO"
        elif self.is_open():
            return "APERTO"
        elif not self.is_open():
            return "NON APERTO"

    def get_state_color(self) -> str: 
        """Get a color associateto to the state"""
        if self.is_closed():
            return "#D42828" # red
        elif self.is_open():
            return "#198754" # green-success
        else:
            return "#6C757D" # muted grey

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
