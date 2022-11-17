from dataclasses import dataclass
@dataclass
class PollOptionDto:
    """
    Poll Option. One of the choices user may 
    choose from.
    Constructor params:
        value: The value of the option.
        key: The key of the option. If the key is not provided, is used value as key.
    """
    value: str
    key: str 
    id: str
    

    def __init__(self, id: str, value: str, key: str=None) -> None:
        self.id = id
        self.value = value
        self.key = key if key is not None else value
