from typing import Any, Mapping, Optional
from apps.polls_management.models.poll_model import PollModel, PollOptionModel

from django.forms import ModelForm, DateTimeInput, HiddenInput
from django.utils.translation import gettext as _


class PollForm(ModelForm):
    """Tool to create a new Poll"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.data.get('poll_type') is None:
            self.data['poll_type'] = PollModel.PollType.SINGLE_OPTION

        # Make votable_mj true by default
        self.fields['votable_mj'].initial = True


    class Meta:
        model = PollModel
        fields=['name','question', 'poll_type', 'open_datetime', 'close_datetime', 'predefined', 'votable_mj']
        labels={
            "name": _("Nome"), 
            "question": _("Quesito"), 
            "poll_type": _("Tipologia"), 
            "open_datetime": _("Data Apertura"), 
            "close_datetime": _("Data Chiusura"),
            "author": _("Nome dell'autore"), 
            "votable_mj": _("Rendi votabile ANCHE con il metodo del Giudizio Maggioritario")
        }
        help_texts={
            "name": _("Un nome sintetico che descrive la scelta"), 
            "question": _("La domanda che vuoi porre al tuo votante"), 
            "poll_type": _("Il metodo che verrà usato per esprimere il voto e calcolare i risultati"), 
            "open_datetime": _("La data dalla quale sarà possibile votare la scelta"), 
            "close_datetime": _("La data dalla quale non sarà più possibile votare la scelta"), 
            "author": _("Il nome dell'autore che ha creato la scelta"),
            "votable_mj": _("(abilita questa opzione se vuoi che un sondaggio a OPZIONE SINGOLA sia votabile ANCHE con il metodo del Giudizio Maggioritario)")
        }
        error_messages = {
            'name': {
                'max_length': _("Il nome inserito è troppo lungo, cerca di essere più sintetico"),
                'required': _("Dai un nome alla tua scelta"), 
            },
            'question': {
                'max_length': _("Il quesito inserito è troppo lungo, cerca di essere più sintetico"),
                'required': _("Inserisci la domanda da chiedere"), 
            },
            'poll_type': {
                'required': _("Seleziona una tipologia di scelta"), 
            },
            'close_datetime': {
                'required': _("Inserisci una data di chiusura per la scelta"), 
            }
        }
        widgets = {
            'open_datetime': DateTimeInput(
                format=('%Y-%m-%d %H:%M'), 
                attrs={
                    'class':'form-control', 
                    'placeholder':'Scegli la data di apertura della scelta', 
                    'type':'datetime-local'
                }
            ),
            'close_datetime': DateTimeInput(
                format=('%Y-%m-%d %H:%M'), 
                attrs={
                    'class':'form-control', 
                    'placeholder':'Scegli la data di chiusura della scelta', 
                    'type':'datetime-local',
                    # 'required':True
                }
            ),
            'predefined': HiddenInput(),
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

    def clean(self):
        open_datetime = self.cleaned_data.get("open_datetime", None)
        close_datetime = self.cleaned_data.get("close_datetime", None)

        if open_datetime is not None and close_datetime is None:
            self._errors['close_datetime'] = self.error_class([
                    'Inserisci anche una data di chisura'])
        elif open_datetime is None and close_datetime is not None:
            self._errors['open_datetime'] = self.error_class([
                    'Inserisci anche una data di apertura'])
        elif open_datetime is not None and close_datetime is not None:
            if open_datetime > close_datetime:
                self._errors['close_datetime'] = self.error_class([
                    'Inserisci una data di chiusura successiva a quella di apertura'])
        
        return self.cleaned_data

# class PollOptionForm(ModelForm):
#     """(Not used) form to input option.
#     TODO: study how to use it properly """
#     class Meta:
#         model = PollOptionModel
#         fields=['value']
#         labels={
#             "value": "Testo opzione"
#         }