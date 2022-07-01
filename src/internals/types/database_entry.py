import json
from dataclasses import dataclass, fields, asdict

from typing import Dict
from src.internals.types import AbstractDataclass


@dataclass
class DatabaseEntry(AbstractDataclass):

    @classmethod
    def from_json(cls, input_json: str):
        output_dict = json.loads(input_json)

        return cls.from_json(output_dict)

    @classmethod
    def from_dict(cls, input_dict: Dict):
        """
        Init a dataclass instance off a dictionary.
        """
        args = {
            key: value
            for key, value in input_dict.items()
            if key in {
                field.name
                for field
                in fields(cls)
            }
        }
        instance = cls(**args)

        return instance

    def to_dict(self):
        return asdict(self)

    def to_json(self):
        return json.dumps(self.to_dict())
