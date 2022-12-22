from django.core.exceptions import ObjectDoesNotExist


class PollHasBeenVotedException(ObjectDoesNotExist):
    """
    A certain Poll can't be deleted because it has already vote
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)

