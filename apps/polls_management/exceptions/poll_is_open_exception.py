from django.core.exceptions import ObjectDoesNotExist


class PollIsOpenException(ObjectDoesNotExist):
    """
    A certain Poll is not open
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)
