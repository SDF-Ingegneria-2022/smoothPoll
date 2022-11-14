
from polls.logic.classes.poll_option import PollOption


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