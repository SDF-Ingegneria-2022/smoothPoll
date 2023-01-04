class PaginatorPageSizeException(Exception):
    """
    Paginator page size not valid.
    """
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
    