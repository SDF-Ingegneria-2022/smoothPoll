from typing import Any, Mapping, Optional
from apps.polls_management.models.poll_model import PollModel, PollOptionModel

from django.forms import ModelForm, DateTimeInput
from django.utils.translation import gettext as _


class PollForm(ModelForm):
    """Tool to create a new Poll"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.data.get('poll_type') is None:
            self.data['poll_type'] = PollModel.PollType.SINGLE_OPTION

    class Meta:
        model = PollModel
        fields=['name','question', 'poll_type', 'open_datetime', 'close_datetime']
        labels={
            "name": _("Nome"), 
            "question": _("Quesito"), 
            "poll_type": _("Tipologia"), 
            "open_datetime": _("Data Apertura"), 
            "close_datetime": _("Data Chiusura"),
        }
        help_texts={
            "name": _("Un nome sintetico che descrive il sondaggio"), 
            "question": _("La domanda che vuoi porre al tuo votante"), 
            "poll_type": _("Il metodo che verrà usato per esprimere il voto e calcolare i risultati"), 
            "open_datetime": _("La data dalla quale sarà possibile votare il sondaggio"), 
            "close_datetime": _("La data dalla quale non sarà più possibile votare il sondaggio"), 
        }
        error_messages = {
            'name': {
                'max_length': _("Il nome inserito è troppo lungo, cerca di essere più sintetico"),
                'required': _("Dai un nome al tuo sondaggio"), 
            },
            'question': {
                'max_length': _("Il quesito inserito è troppo lungo, cerca di essere più sintetico"),
                'required': _("Inserisci la domanda per il tuo sondaggio"), 
            },
            'poll_type': {
                # 'required': _("Seleziona una tipologia di sondaggio"), 
            },
            'close_datetime': {
                'required': _("Inserisci una data di chiusura per il sondaggio"), 
            }
        }
        widgets = {
            'open_datetime': DateTimeInput(
                format=('%Y-%m-%d %H:%M'), 
                attrs={
                    'class':'form-control', 
                    'placeholder':'Scegli la data di apertura del sondaggio', 
                    'type':'datetime-local'
                }
            ),
            'close_datetime': DateTimeInput(
                format=('%Y-%m-%d %H:%M'), 
                attrs={
                    'class':'form-control', 
                    'placeholder':'Scegli la data di chiusura del sondaggio', 
                    'type':'datetime-local',
                    'required':True
                }
            ),
        }

    def get_min_options(self) -> int: 
        """Get poll min options (according to poll_type)"""

        if self.data.get("poll_type") == PollModel.PollType.MAJORITY_JUDJMENT:
            return 3
        return 2

    def get_type_verbose_name(self) -> str:
        """Get verbose name of current poll_type 
        (the one you may display on UI)"""

        return PollModel(
            name = self.data["name"], 
            question = self.data["question"], 
            poll_type = self.data["poll_type"],
            ).get_type_verbose_name()


# class PollOptionForm(ModelForm):
#     """(Not used) form to input option.
#     TODO: study how to use it properly """
#     class Meta:
#         model = PollOptionModel
#         fields=['value']
#         labels={
#             "value": "Testo opzione"
#         }