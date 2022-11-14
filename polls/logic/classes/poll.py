
from polls.logic.classes.poll_option import PollOption

class PollOptionUnvalidException(Exception):
    """
    A PollOption is unvalid for a certain Poll
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)
    pass

class Poll: 
    """
    A classic poll, where user may choose one between 
    a set of options. 

    Options are ranke in decreasing number of votes. 
    """

    name: str
    question: str
    options: list[PollOption]

    def __init__(self, name: str, question: str, options: list[PollOption]) -> None: 
        self.name = name
        self.question = question
        self.options = options.copy()

    def get_option_by_key(self, key: str) -> PollOption:
        
        for option in self.options:
            if option.key == key:
                return option
        
        raise PollOptionUnvalidException()

# dummy poll with all options
dummy_poll = Poll(
    "Sondaggio di prova", 
    "Quale tra queste User Story ti sembra più importante da implementare?", 
    [
        PollOption("User Story Nro #01"), 
        PollOption("User Story Nro #02"), 
        PollOption("User Story Nro #03")
    ]
)