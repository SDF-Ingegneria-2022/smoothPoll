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
        error_messages = {
            'name': {
                'max_length': "Il nome inserito è troppo lungo, cerca di essere più sintetico",
                'required': "Dai un nome al tuo sondaggio", 
            },
            'question': {
                'max_length': "Il quesito inserito è troppo lungo, cerca di essere più sintetico",
                'required': "Inserisci la domanda per il tuo sondaggio", 
            },
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