from dataclasses import dataclass


@dataclass
class TestObjectDTO:
    __test__ = False  # prevents pytest collection
    name: str
    domain: str
    project: str
    instance: str
