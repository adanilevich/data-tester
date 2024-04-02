from typing import List

from src.testcase.driven_ports.i_backend import IBackend


class DummyBackend(IBackend):
    """Dummy backend for test purpose only"""

    def get_testobjects(self, domain: str, project: str, instance) -> List[str]:
        return ["testobject1", "testobject2"]
