from typing import Any, Dict, Self
from pydantic import BaseModel


class DTO(BaseModel):

    @classmethod
    def from_dict(cls, dict_: dict) -> Self:  # mytype: ignore-error
        return cls(**dict_)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()

    def to_json(self) -> str:
        return self.model_dump_json()

    def create_copy(self) -> Self:
        return self.model_copy()
