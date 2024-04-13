from typing import List, Dict, Any, Optional, Tuple

from src.testcase.driven_ports.i_backend import IBackend
from src.dtos.specifications import SchemaSpecificationDTO


class DummyBackend(IBackend):
    """Dummy backend for test purpose only"""

    def get_testobjects(self, domain: str, stage: str, instance: str) -> List[str]:
        return ["testobject1", "testobject2"]

    def get_schema(self, domain: str, stage: str, instance: str,
                   testobject: str) -> SchemaSpecificationDTO:
        return SchemaSpecificationDTO(columns={"my_col": "my_dtype"})

    def harmonize_schema(self, schema: SchemaSpecificationDTO) -> SchemaSpecificationDTO:
        return schema

    def run_query(self, query: str, domain: str, stage: str, instance: str) \
            -> Dict[str, List[Any]]:
        return {"col": [1, 2, 3]}

    def get_rowcount(self, domain: str, stage: str, instance: str, testobject: str,
                     filters: Optional[List[Tuple[str, str]]] = None) -> int:
        return 10
