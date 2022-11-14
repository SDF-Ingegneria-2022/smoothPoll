
from polls.logic.classes.poll_option import PollOption


class Poll: 
    """
    A classic poll, where user may choose one between 
    a set of options. 

    Options are ranke in decreasing number of votes. 
    """

    name: str
    question: str

    __options: list[PollOption]

    def __init__(self, name: str, question: str, options: list[PollOption]) -> None: 
        self.name = name
        self.question = question
        self.__options = options.copy()

    def get_options(self) -> list[PollOption]:
        return self.__options.copy()

    def add_option(self, option: PollOption) -> None:
        self.__options.append(option)

    def remove_option(self, option: PollOption) -> None:
        self.__options.remove(option)


         