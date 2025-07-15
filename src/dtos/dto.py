from typing import Any, Dict, Literal, Self
from pydantic import BaseModel


class DTO(BaseModel):
    @classmethod
    def from_dict(cls, dict_: dict) -> Self:  # mytype: ignore-error
        return cls(**dict_)

    def to_dict(
        self,
        exclude: set | None = None,
        mode: Literal["json", "python"] = "python",
    ) -> Dict[str, Any]:
        return self.model_dump(exclude=exclude, mode=mode)

    def to_json(self, exclude: set | None = None) -> str:
        return self.model_dump_json(exclude=exclude)

    def create_copy(self) -> Self:
        return self.model_copy()

    @classmethod
    def from_json(cls, json_: str | bytes | bytearray) -> Self:
        return cls.model_validate_json(json_)
