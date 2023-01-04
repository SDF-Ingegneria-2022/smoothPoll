from django.core.exceptions import ObjectDoesNotExist


class PollCannotBeOpenedException(ObjectDoesNotExist):
    """
    A certain Poll cannot be opened
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)
