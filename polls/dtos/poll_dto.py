
from typing import List
from dataclasses import dataclass

from polls.dtos.poll_option_dto import PollOptionDto
from polls.exceptions.poll_option_unvalid_exception import PollOptionUnvalidException
@dataclass
class PollDto: 
    """
    A classic poll, where user may choose one between 
    a set of options. 

    Options are ranke in decreasing number of votes. 
    """
    
    name: str
    question: str
    options: List[PollOptionDto]

    def get_option_by_key(self, key: str) -> PollOptionDto:
        
        for option in self.options:
            if option.key == key:
                return option
        
        raise PollOptionUnvalidException()

# dummy poll with all options
dummy_poll = PollDto(
    "Sondaggio di prova", 
    "Quale tra queste User Story ti sembra più importante da implementare?", 
    [
        PollOptionDto("User Story Nro #01"), 
        PollOptionDto("User Story Nro #02"), 
        PollOptionDto("User Story Nro #03")
    ]
)