from polls.models.poll_option_model import PollOptionModel
from django.forms import ModelForm

class PollForm(ModelForm):
    class Meta:
        model = PollOptionModel
        fields="__all__"
        labels={
            "value": "Valore opzione", 
        }
