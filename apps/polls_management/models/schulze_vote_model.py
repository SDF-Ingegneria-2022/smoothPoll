from typing import List
from apps.polls_management.exceptions.poll_option_model_does_not_exist_exception import PollOptionDoesNotExist
from apps.polls_management.exceptions.poll_option_number_mismatch_exception import PollOptionNumberMismatch
from apps.polls_management.exceptions.wrong_poll_options_exception import WrongPollOptions
from apps.polls_management.models.poll_option_model import PollOptionModel
from apps.polls_management.constants.models_constants import POLL_MODEL_NAME
from django.db.models import CharField
from django.db import models
from django.core.exceptions import ObjectDoesNotExist

class SchulzeVoteModel(models.Model):
    """Class representing the vote for a Schulze poll"""

    datetime: models.DateTimeField = models.DateTimeField(auto_now=True)
    """Timestamp of vote registration instant"""

    poll: models.ForeignKey = models.ForeignKey(POLL_MODEL_NAME, on_delete=models.CASCADE)
    """Reference to poll"""

    order: CharField = models.CharField(max_length=200)
    """String representation of order for poll options classification"""

    def __str__(self):
        return str({
            'id': self.id,
            'datetime': self.datetime, 
            'poll': str(self.poll),
            'order': str(self.order)
        })

    def get_order_as_obj(self) -> List[PollOptionModel]:
        """method to retrieve all Schulze poll related options as objects"""

        return list(PollOptionModel.objects.filter(poll_fk=self.poll).order_by('id'))

    def get_order(self) -> List[str]:
        """Method used to get list of user ordered poll options as strings of their ids"""

        # order is a string like this "1,2,3" so we get the order as a list of string ids like this ["1","2","3"]
        order_ids = self.order.split(',')

        return order_ids
    
    def get_order_as_ids(self) -> List[str]:
        """Method used to get list of all poll options as strings of their ids"""

        order_ids = self.order.split(',')
        order_ids.sort()

        return order_ids
    
    def set_order(self, input_order: List[int]):
        """Method used to set the order of the poll options from the input"""

        # first some checks to make sure input_order is legit (option exists, is related to poll, all options and not repated)
        try:
            for option_id in input_order:
                option = PollOptionModel.objects.get(id=option_id)
        except ObjectDoesNotExist:
            raise PollOptionDoesNotExist(f"Error: poll option with id={option_id} does not exit.")
        
        all_options = PollOptionModel.objects.filter(poll_fk=self.poll)
        all_options_ids = list(all_options.values_list('id', flat=True))
        all_options_ids.sort()
        sorted_input: List[int] = input_order.copy()
        sorted_input.sort()

        if len(input_order) != all_options.count():
            raise PollOptionNumberMismatch(f"Error: the number of poll options and input ids do not match.")

        if all_options_ids != sorted_input:
            raise WrongPollOptions(f"Error: the poll options given as input don't belong to the poll of id={self.poll.id}")

        order_str: str = ""

        # set order from the input, for example [1, 2, 3] to "1,2," except last element
        for id in input_order[:-1]:
            order_str += str(id)
            order_str += ","

        # set last element of input_order to the string (to not get a string like this "1,2,3,")
        order_str += str(input_order[-1])

        self.order = order_str

