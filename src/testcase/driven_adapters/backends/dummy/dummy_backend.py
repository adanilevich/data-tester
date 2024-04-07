from typing import List

from src.testcase.driven_ports.i_backend import IBackend, SchemaDTO


class DummyBackend(IBackend):
    """Dummy backend for test purpose only"""

    def get_testobjects(self, domain: str, project: str, instance: str) -> List[str]:
        return ["testobject1", "testobject2"]

    def get_schema(self, domain: str, project: str, instance: str,
                   testobject: str) -> SchemaDTO:
        return SchemaDTO(columns={"my_col": "my_dtype"})

    def harmonize_schema(self, schema: SchemaDTO) -> SchemaDTO:
        return schema
