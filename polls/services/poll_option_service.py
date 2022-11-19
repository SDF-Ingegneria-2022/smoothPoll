from typing import List, cast
from polls.dtos.poll_option_dto import PollOptionDto
from polls.models.poll_option_model import PollOptionModel


class PollOptionService:
    """Service for handle poll options."""

    @staticmethod
    def create(key: str, value: str, poll_id: str) -> PollOptionDto:
        """Creates a new poll option.
        Args:
            key: Key of the option.
            value: Value of the option.
            poll_id: Id of the poll.
        Returns:
            PollOptionDto: The created poll option.
        """
        new_option: PollOptionModel = PollOptionModel(key=key, value=value, poll_fk_id=poll_id)
        new_option.save()

        return PollOptionDto(id=new_option.id, key=new_option.key, value=new_option.value)

    @staticmethod
    def get_by_poll_id(poll_id: str) -> List[PollOptionDto]:
        """Get a poll option by its id.
        Args:
            id: Id of the option.
        Returns:
            PollOptionDto: List of poll options that satify the id.
        """
        poll_options: List[PollOptionModel] =  PollOptionModel.objects.filter(poll_fk=poll_id)
        return  [PollOptionDto(id=poll_option.id, key = poll_option.key, value=poll_option.value )for  poll_option in poll_options]