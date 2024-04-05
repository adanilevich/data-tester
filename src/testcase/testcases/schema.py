from typing import List, Optional, Dict
from dataclasses import dataclass, asdict, field

from src.testcase.testcases.abstract_testcase import AbstractTestCase


@dataclass
class DiffEntry:
    expected_col: Optional[str] = None
    expected_dtype: Optional[str] = None
    actual_col: Optional[str] = None
    actual_dtype: Optional[str] = None
    result_col: Optional[str] = None
    result_dtype: Optional[str] = None
    result_all: Optional[str] = None


@dataclass
class Diff:
    diffs: List[DiffEntry] = field(default_factory=lambda: [])

    def dict(self) -> List[Dict[str, str]]:
        return [asdict(diff_entry) for diff_entry in self.diffs]


class SchemaTestCase(AbstractTestCase):
    """This testcase always returns ok -- test purpose only."""
    ttype = "SCHEMA"
    required_specs = ["schema"]
    preconditions = ["testobject_exists"]

    def _execute(self):

        actual_schema = self._get_actual_schema()

        expected_schema = self._get_expected_schema()
        if expected_schema is None:
            self.status = self.status.ABORTED
            self.result = self.result.NA
            return None

        self.diff = self._compare_schemas(exp=expected_schema, act=actual_schema).dict()
        self.add_detail({"Diff": str(self.diff)})

        if len(self.diff) > 0:
            self.result = self.result.NOK
            self.update_summary("Testobject schema differs from specification.")
        else:
            self.result = self.result.OK
            self.update_summary("Specified schema and testobject are equal.")

        return None

    def _get_actual_schema(self) -> List[Dict[str, str]]:
        self.notify(f"Getting data object schema for {self.testobject.name}")
        result_schema_raw = self.backend.get_schema(
            domain=self.testobject.domain,
            project=self.testobject.project,
            instance=self.testobject.instance,
            testobject=self.testobject.name
        )
        result_schema = self.backend.harmonize_schema(result_schema_raw)
        return result_schema.dict()

    def _get_expected_schema(self) -> Optional[List[Dict[str, str]]]:
        self.notify(f"Getting expected schema for {self.testobject.name}")
        # unpack expected schema from provided specifications
        provided_schema_specs: List[List[Dict[str, str]]] = []
        expected_schema: List[Dict[str, str]] = []
        for spec in self.specs:
            if spec.type == "schema":
                if isinstance(spec.content, list):
                    expected_schema = spec.content
                    provided_schema_specs.append(expected_schema)

        # if more than one schema spec is provided, abort execution.
        # But: we don't check for 'no specs provided' since this is done by precon checks
        if len(provided_schema_specs) > 1:
            msg = "Testcase stopped: more than one schema spec provided!"
            self.update_summary(msg)
            self.add_detail({"Provided schema specs": str(provided_schema_specs)})
            self.notify(msg)
            return None

        return expected_schema

    def _compare_schemas(self, exp: List[Dict[str, str]], act: List[Dict[str, str]]) \
            -> Diff:
        """
        Returns a diff as list of dicts with keys 'expected_col', 'expected_dtype',
        'actual_col', 'actual_dtype', 'result_col', 'result_dtype', 'result_all', where
        'result_' cols take values 'OK', 'NOK', 'N/A' and reflect comparison results.
        """

        for col_dtype in exp:
            diff_entry = DiffEntry(result_col="N",)
            expected_col, expected_dtype = col_dtype.items()
            diff_entry.expected_col = expected_col
            diff_entry.expected_dtype = expected_dtype
            if col_dtype in act:
                actual_col, actual_dtype = col_dtype.items()
                if actual_col == expected_col:
                    diff_entry.actual_col = actual_col
                    diff_entry.result_col = "OK"
                    if actual_dtype == expected_dtype:
                        diff_entry.actual_dtype = actual_dtype
                        diff_entry.result_dtype = "OK"

        # TODO: implement this
        a = self.backend
        return []
