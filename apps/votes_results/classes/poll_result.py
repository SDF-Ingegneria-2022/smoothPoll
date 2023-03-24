from typing import List
from dataclasses import dataclass
from typing import Optional
from apps.polls_management.models.poll_model import PollModel
from apps.polls_management.models.poll_option_model import PollOptionModel
from apps.polls_management.models.vote_model import VoteModel

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
    position:int
    """
    Position in results
    """


    def __init__(self, poll_option: PollOptionModel) -> None:
        self.n_votes = PollResultVoice.__count_n_votes(poll_option)
        self.position = 0
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


        index =0 
        aux_n_position=[]
        pos = 1 #temporary position
        n_pos = 1 #number of option on the same position
        for option in self.__memoized_result:
            if(index==0):
                option.position=pos
            elif(self.__memoized_result[index-1].n_votes==option.n_votes):
                option.position=pos
                n_pos+=1
            else:
                pos += n_pos
                option.position = pos
                n_pos=1
            aux_n_position.append([pos,option])
            index += 1

        print(aux_n_position)

        
        index = 0
        n_position=[]
        while index <len(aux_n_position)-1:
            print(index)
            print(aux_n_position[index][0],aux_n_position[index+1][0])
            print(aux_n_position[index][1],aux_n_position[index+1][1])
            if(aux_n_position[index][0]!=aux_n_position[index+1][0]):
                n_position.append(aux_n_position[index])
            index+=1
        n_position.append(aux_n_position[-1])
        return {"results":self.__memoized_result
                #"positions":n_position
                }