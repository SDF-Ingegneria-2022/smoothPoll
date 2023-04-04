import random
from django.conf import settings
from apps.polls_management.models.poll_option_model import PollOptionModel
from typing import List
from django.db import models
from django.db.models import CharField
from django.utils.translation import gettext as _
from django.utils import timezone


# Poll model fields
NAME = 'name'
QUESTION = 'question'
POLL_TYPE = 'poll_type'
OPEN_DATETIME = 'open_datetime'
CLOSE_DATETIME = 'close_datetime'
PREDEFINITED = 'predefined'
VOTABLE_MJ = 'votable_mj'
AUTHOR = 'author'
PRIVATE = 'private'
SHORT_ID = 'short_id'
RANDOMIZE_OPTIONS = 'randomize_options'
VOTABLE_TOKEN = 'votable_token'
PROTECTION = 'protection'
class PollModel(models.Model): 

    class PollType(models.TextChoices):
        """Possible vode modes a PollModel can 
        be voted. In this system, each PollModel 
        belongs to one PollType"""
        SINGLE_OPTION = 'single_option', _('Opzione Singola')
        MAJORITY_JUDJMENT = 'majority_judjment', _('Giudizio Maggioritario')
        
    class PollVoteProtection(models.TextChoices):
        """Possible vote protection modes a poll can have"""
        UNPROTECTED = 'unprotected', _('Non protetto')
        TOKEN = 'token', _('Giudicabile tramite Token')

    name: CharField = models.CharField(
        max_length=200, verbose_name=_('Nome Scelta'))

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
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        default=None, blank=True, null=True,
    )
    
    private: models.BooleanField = models.BooleanField(
        default=False, verbose_name=_("Scelta privata")
    )
    
    short_id: models.CharField = models.CharField(
        max_length=60, verbose_name=_("ID Corto"), 
        default=None, blank=True, null=True, unique=True
    )
    
    randomize_options: models.BooleanField = models.BooleanField(
        default=False, verbose_name=_("Randomizza Opzioni")
    )
    
    # TODO: remove afer related changes
    votable_token: models.BooleanField = models.BooleanField(
        default=False, verbose_name=_("Votabile con Token")
    )
    
    protection: models.CharField = models.CharField(
        max_length=200,
        choices=PollVoteProtection.choices, 
        default=PollVoteProtection.UNPROTECTED
        )  

    def __str__(self):
        return str({
            'id': self.id, 
            NAME: self.name,
            QUESTION: self.question,
            POLL_TYPE: self.poll_type, 
            OPEN_DATETIME: self.open_datetime, 
            CLOSE_DATETIME: self.close_datetime,
            PREDEFINITED: self.predefined,
            PRIVATE:  self.private,
            SHORT_ID: self.short_id,
            RANDOMIZE_OPTIONS: self.randomize_options,
            VOTABLE_TOKEN: self.votable_token,
            PROTECTION: self.protection
        })

    def options(self) -> List[PollOptionModel]:
        options = list(PollOptionModel.objects.filter(poll_fk=self.id))
        if self.randomize_options:
            random.shuffle(options)
       
        return options


    def is_open(self) -> bool:
        """Check if Poll is open"""

        if self.open_datetime is None:
            return False

        return timezone.now() > self.open_datetime

    def is_closed(self) -> bool:
        """Check if Poll is closed"""
        
        if self.close_datetime is None:
            return False
        
        return timezone.now() > self.close_datetime
    
    def is_votable_token(self) -> bool:
        """Check if Poll is votable with token

        Returns:
            bool: True if votable with token, False otherwise
        """
        return self.protection == PollModel.PollVoteProtection.TOKEN
    
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
