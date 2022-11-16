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
    

    def __init__(self, value: str, key: str=None) -> None:
        self.value = value
        self.key = key if key is not None else value
