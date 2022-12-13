from polls.models.poll_model import PollModel, PollOptionModel

from django.forms import ModelForm

class PollForm(ModelForm):
    class Meta:
        model = PollModel
        fields=['name','question']
        labels={
            "name": "Nome", 
            "question": "Quesito"
        }


class PollOptionForm(ModelForm):
    class Meta:
        model = PollOptionModel
        fields=['value']
        labels={
            "value": "Testo opzione"
        }