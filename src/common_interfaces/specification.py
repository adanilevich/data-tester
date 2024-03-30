from dataclasses import dataclass
from typing import Union, Any


@dataclass
class SpecificationDTO:
    type: str
    content: Any
    location: str
    valid: Union[bool, None] = None
