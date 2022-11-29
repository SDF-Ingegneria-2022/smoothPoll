from polls.models.poll_model import PollModel
from django.forms import ModelForm

class PollForm(ModelForm):
    class Meta:
        model = PollModel
        fields="__all__"
        labels={
            "name": "Nome", 
            "question": "Quesito"
        }
