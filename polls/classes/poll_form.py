from typing import Any, Mapping, Optional
from polls.models.poll_model import PollModel, PollOptionModel

from django.forms import ModelForm
from django.utils.translation import gettext as _


class PollForm(ModelForm):
    """Tool to create a new Poll"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.data.get('poll_type') is None:
            self.data['poll_type'] = PollModel.PollType.SINGLE_OPTION

    class Meta:
        model = PollModel
        fields=['name','question', 'poll_type']
        labels={
            "name": _("Nome"), 
            "question": _("Quesito"), 
            "poll_type": _("Tipologia"), 
        }
        help_texts={
            "name": _("Un nome sintetico che descrive il sondaggio"), 
            "question": _("La domanda che vuoi porre al tuo votante"), 
            "poll_type": _("Il metodo che verrà usato per esprimere il voto e calcolare i risultati"), 
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
            }
        }

# class PollOptionForm(ModelForm):
#     """(Not used) form to input option.
#     TODO: study how to use it properly """
#     class Meta:
#         model = PollOptionModel
#         fields=['value']
#         labels={
#             "value": "Testo opzione"
#         }