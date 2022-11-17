from typing import List
from dataclasses import dataclass
from typing import Optional
from polls.models.poll_model import PollModel
from polls.models.poll_option_model import PollOptionModel
from polls.models.vote_model import VoteModel

@dataclass
class PollResultVoice:
    """
    A single voice of the result. It's made of a PollOption and the number
    of received votes.

    N votes are calculated during object building.
    """

    n_votes: int
    """
    Number of votes the option received
    """

    option: PollOptionModel
    """
    The voted option
    """

    def __init__(self, poll_option: PollOptionModel) -> None:
        self.n_votes = PollResultVoice.__count_n_votes(poll_option)
        self.option = poll_option

    @staticmethod
    def __count_n_votes(poll_option: PollOptionModel) -> int:
        return VoteModel.objects.filter(poll_option=poll_option.id).count()


@dataclass
class PollResult: 
    """
    Compute a result of a closed poll. 
    """

    poll: PollModel
    """
    The poll the result is about
    """


    def __init__(self, poll: PollModel) -> None:
        self.poll: PollModel = poll
        self.__memoized_result: Optional[List[PollResultVoice]] = None

    def get_sorted_options(self) -> List[PollResultVoice]:
        """
        Result as an ordered list of pairs (choice, n_votes).

        Result is computed only once for efficiency reasons (and then memoized). 
        If you want to compute it again, create another PollResult instance.
        """

        # if it exists, return memoized result
        if self.__memoized_result is not None:
            return self.__memoized_result

        # calculate result
        self.__memoized_result = []
        for option in PollOptionModel.objects.filter(poll_fk=self.poll.id).all():
            self.__memoized_result.append(PollResultVoice(option))

        # sort by (decreasing) n votes
        def n_votes(voice: PollResultVoice):
            return voice.n_votes
        self.__memoized_result.sort(reverse=True, key=n_votes)

        return self.__memoized_result