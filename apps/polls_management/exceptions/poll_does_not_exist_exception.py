from django.core.exceptions import ObjectDoesNotExist


class PollDoesNotExistException(ObjectDoesNotExist):
    """
    A certain Poll doesn't exist.
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)
