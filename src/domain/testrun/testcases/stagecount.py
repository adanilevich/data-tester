from typing import Optional

from . import AbstractTestCase, TestCaseError
from src.dtos import (
    StagecountSpecDTO,
    DBInstanceDTO,
    TestType,
    TestResult,
    Importance,
)


class StageCountTestCaseError(TestCaseError):
    """Exception raised when a stagecount testcase operation fails."""


class StageCountTestCase(AbstractTestCase):
    """
    Testcase counts rows in a staging table (filtered by newest m__ts) and compares
    to line counts of the corresponding raw file(s) to catch loading errors.
    """

    ttype = TestType.STAGECOUNT
    required_specs = []
    preconditions = ["testobject_exists", "testobject_not_empty"]

    def _execute(self):
        spec: Optional[StagecountSpecDTO] = self._get_spec()
        if spec and spec.location:
            self.add_fact({"Specification": spec.location.path})

        db = DBInstanceDTO.from_testobject(self.testobject)

        # 1. Query stage table for newest load
        self.notify("Querying stage table for newest load")
        stage_rowcount, source_file_path = self._get_stage_load_info(db)
        self.add_fact({"Source file path": source_file_path})
        self.add_detail({"Stage rowcount": stage_rowcount})

        # 2. Count raw file rows using full path from stage table
        self.notify(f"Counting rows in raw file: {source_file_path}")
        encoding: Optional[str] = spec.raw_file_encoding if spec else None
        skip_lines: Optional[int] = spec.skip_lines if spec else None
        self.add_detail({"Encoding": encoding or "inferred by backend"})
        self.add_detail({"Skip lines": f"{skip_lines or 'inferred by backend'}"})
        raw_testobject = self.backend.get_raw_testobject(self.testobject)
        raw_rowcount: int = self.backend.get_testobject_rowcount(
            testobject=raw_testobject,
            filters=[("filepath", f"={source_file_path}")],
            encoding=encoding,
            skip_lines=skip_lines,
        )
        self.add_detail({"Raw file rowcount": raw_rowcount})

        # 3. Compare
        self._evaluate_results(stage_rowcount, raw_rowcount)

    def _get_spec(self) -> Optional[StagecountSpecDTO]:
        for spec in self.specs or []:
            if isinstance(spec, StagecountSpecDTO):
                return spec
        return None

    def _get_stage_load_info(self, db: DBInstanceDTO) -> tuple[int, str]:
        """Query stage table for rows with newest m__ts.

        Returns (rowcount, source_file, source_file_path).
        """
        table = self.testobject.name
        query = self.backend.translate_query(
            f"""
            SELECT
                COUNT(*) AS __cnt__,
                MAX(m__source_file_path) AS __src_path__
            FROM {table}
            WHERE m__ts = (SELECT MAX(m__ts) FROM {table})
            """,
            db,
        )
        self.add_detail({"Stage query": query})
        result = self.backend.run_query(query, db)
        result_dict = result.to_dict(as_series=False)

        count: int = result_dict["__cnt__"][0]
        source_file_path: str = result_dict["__src_path__"][0]
        if not source_file_path:
            raise StageCountTestCaseError("m__source_file_path is empty for newest load.")
        return count, source_file_path

    def _evaluate_results(self, stage_count: int, raw_count: int):
        if stage_count == raw_count:
            self.result = TestResult.OK
            self.summary = f"Stage rowcount ({stage_count}) matches raw file count"
        else:
            self.result = TestResult.NOK  # type: ignore[assignment]
            self.summary = f"Stage ({stage_count}) and raw ({raw_count}) counts  differ"
            diff = {
                "stagecount_diff": {
                    "stage_rowcount": stage_count,
                    "raw_file_rowcount": raw_count,
                }
            }
            self.diff.update(diff)
            self.notify(self.summary, importance=Importance.WARNING)
