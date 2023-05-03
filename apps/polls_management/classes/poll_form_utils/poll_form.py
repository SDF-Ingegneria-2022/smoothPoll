from apps.polls_management.models.poll_model import RANDOMIZE_OPTIONS, PollModel, NAME, \
                                                    QUESTION, POLL_TYPE, \
                                                    OPEN_DATETIME, CLOSE_DATETIME,\
                                                    PREDEFINITED, VOTABLE_MJ, AUTHOR,\
                                                    PRIVATE, SHORT_ID, PROTECTION, RESULTS_VISIBILITY
from django.forms import ModelForm, DateTimeInput, HiddenInput
from django.utils.translation import gettext as _
from apps.polls_management.classes.poll_form_utils.short_id_util import ShortIdUtil

class PollForm(ModelForm):
    """Tool to create a new Poll"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.data.get(POLL_TYPE) is None:
            self.data[POLL_TYPE] = PollModel.PollType.SINGLE_OPTION

        # Make votable_mj true by default
        self.fields[VOTABLE_MJ].initial = True

        # if not already there, generate a short ID
        self.fields[SHORT_ID].initial = ShortIdUtil.generate()
        if self.data.get(SHORT_ID) is None:
            self.data[SHORT_ID] = ShortIdUtil.generate()
            
        # Randomize options by default
        self.fields[RANDOMIZE_OPTIONS].initial = True
        
        # Protection 
        if self.data.get(PROTECTION) is None:
            self.data[PROTECTION] = PollModel.PollVoteProtection.UNPROTECTED
        self.fields[PROTECTION].initial = PollModel.PollVoteProtection.UNPROTECTED

        # Results visibility
        if self.data.get(RESULTS_VISIBILITY) is None:
            self.data[RESULTS_VISIBILITY] = PollModel.PollResultsVisibility.ALWAYS_VISIBLE
        self.fields[RESULTS_VISIBILITY].initial = PollModel.PollResultsVisibility.ALWAYS_VISIBLE
        

    class Meta:
        model = PollModel
        
        fields = [  NAME,
                    QUESTION, 
                    POLL_TYPE,
                    OPEN_DATETIME, 
                    CLOSE_DATETIME, 
                    PREDEFINITED, 
                    VOTABLE_MJ, 
                    PRIVATE, 
                    SHORT_ID, 
                    RANDOMIZE_OPTIONS,
                    PROTECTION, 
                    RESULTS_VISIBILITY, 
                ]
        
        labels = {
                    NAME: _("Nome"), 
                    QUESTION: _("Quesito"), 
                    POLL_TYPE: _("Tipologia"), 
                    OPEN_DATETIME: _("Data Apertura"), 
                    CLOSE_DATETIME: _("Data Chiusura"),
                    AUTHOR: _("Nome dell'autore"), 
                    VOTABLE_MJ: _("Rendi giudicabile anche con il Giudizio Maggioritario"),
                    PRIVATE: _("Scelta accessibile solo tramite link"), 
                    SHORT_ID: _("Codice identificativo"),
                    RANDOMIZE_OPTIONS: _("Durante la fase di scelta o giudizio le opzioni saranno presentate in ordine casuale"),
                    PROTECTION: _("Tipo di protezione della scelta"), 
                    RESULTS_VISIBILITY: _("Visibilità dei risultati"),
                }
        
        help_texts = {
                        NAME: _("Un nome sintetico che descrive la scelta"), 
                        QUESTION: _("Quesito che verrà posto a chi compie la scelta"), 
                        POLL_TYPE: _("Il metodo che verrà usato per esprimere la scelta e calcolare i risultati"), 
                        OPEN_DATETIME: _("La data dalla quale sarà possibile esprimere la scelta"), 
                        CLOSE_DATETIME: _("La data dalla quale non sarà più possibile esprimere la scelta"), 
                        AUTHOR: _("Il nome dell'autore che ha creato la scelta"),
                        VOTABLE_MJ: _("(abilita questa opzione se vuoi che una scelta a Opzione Singola sia giudicabile anche con il Giudizio Maggioritario)"),
                        PRIVATE: _("(se abiliti questa opzione la scelta non sarà visibile nella sezione con tutte le scelte)"),
                        SHORT_ID: _("Codice identificativo univoco per il link"), 
                        PROTECTION: _("Come evitare che la scelta venga effetuata più volte dallo stesso utente"), 
                        RESULTS_VISIBILITY: _("Quando possono essere visualizzati i risultati della scelta"),
                    }
        
        error_messages = {
            NAME: {
                'max_length': _("Il nome inserito è troppo lungo, cerca di essere più sintetico"),
                'required': _("Dai un nome alla tua scelta"), 
            },
            QUESTION: {
                'max_length': _("Il quesito inserito è troppo lungo, cerca di essere più sintetico"),
                'required': _("Inserisci la domanda da chiedere"), 
            },
            POLL_TYPE: {
                'required': _("Seleziona una tipologia di scelta"), 
            },
            CLOSE_DATETIME: {
                'required': _("Inserisci una data di chiusura per la scelta"), 
            }, 
        }
        widgets = {
            OPEN_DATETIME: DateTimeInput(
                format=('%Y-%m-%d %H:%M'), 
                attrs={
                    'class':'form-control', 
                    'placeholder':'Scegli la data di apertura della scelta', 
                    'type':'datetime-local'
                }
            ),
            CLOSE_DATETIME: DateTimeInput(
                format=('%Y-%m-%d %H:%M'), 
                attrs={
                    'class':'form-control', 
                    'placeholder':'Scegli la data di chiusura della scelta', 
                    'type':'datetime-local',
                    # 'required':True
                }
            ),
            PREDEFINITED: HiddenInput(),
        }

    def get_min_options(self) -> int: 
        """Get poll min options (according to poll_type)"""
        return 2

    def get_type_verbose_name(self) -> str:
        """Get verbose name of current poll_type 
        (the one you may display on UI)"""

        return PollModel(
            name = self.data[NAME], 
            question = self.data[QUESTION], 
            poll_type = self.data[POLL_TYPE],
            ).get_type_verbose_name()

    def clean(self):

        # checks on open and close datetime
        open_datetime = self.cleaned_data.get(OPEN_DATETIME, None)
        close_datetime = self.cleaned_data.get(CLOSE_DATETIME, None)

        if open_datetime is not None and close_datetime is None:
            self._errors[CLOSE_DATETIME] = self.error_class([
                    'Inserisci anche una data di chisura'])
        elif open_datetime is None and close_datetime is not None:
            self._errors[OPEN_DATETIME] = self.error_class([
                    'Inserisci anche una data di apertura'])
        elif open_datetime is not None and close_datetime is not None:
            if open_datetime > close_datetime:
                self._errors[CLOSE_DATETIME] = self.error_class([
                    'Inserisci una data di chiusura successiva a quella di apertura'])
                
        # checks on short id (used in URL)
        short_id = ShortIdUtil(self.cleaned_data.get(SHORT_ID, ""), poll=self.instance)

        if not short_id.validate_length():
            self._errors[SHORT_ID] = self.error_class(['Il codice deve avere tra i 6 e i 60 caratteri'])
        elif not short_id.validate_characters():
            self._errors[SHORT_ID] = self.error_class(['Il codice deve essere formato solo da lettere e numeri'])
        elif not short_id.validate_uniqness():
            self._errors[SHORT_ID] = self.error_class(['Codice già in uso, prova un altro'])
        
        return self.cleaned_data
