from typing import Any, Dict
from pydantic import BaseModel


class DTO(BaseModel):

    @classmethod
    def from_dict(cls, dto_as_dict: dict) -> Any:  # 'Any' to not clash with subtypes
        return cls(**dto_as_dict)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()

    def to_json(self) -> str:
        return self.model_dump_json()

    def create_copy(self) -> Any:  # 'Any' to not clash with subtypes
        return self.model_copy()
