from dataclasses import dataclass
from abc import ABC


@dataclass
class AbstractDataclass(ABC):
    """
    Prevents abstract dataclasses from being instantiated.
    Source:
    https://stackoverflow.com/questions/60590442/abstract-dataclass-without-abstract-methods-in-python-prohibit-instantiation
    """
    def __new__(cls, *args, **kwargs):
        if cls == AbstractDataclass or cls.__bases__[0] == AbstractDataclass:
            raise TypeError("Cannot instantiate abstract class.")
        return super().__new__(cls)
