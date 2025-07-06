from src.dtos.reports import ReportArtifactDTO
from src.report.adapters.plugins.formatters.default import IReportNamingConventions
from src.dtos import ArtifactType, TestCaseReportArtifactDTO


timeformat = "%Y-%m-%d_%H:%M:%S"


class DefaultReportNamingConventions(IReportNamingConventions):
    """
    Sets testrun report filename by testrun_id and start_ts.
    Sets testcase report filename by testobject, testcase and start_ts.
    """

    def filename(self, artifact: ReportArtifactDTO) -> str:

        if isinstance(artifact, TestCaseReportArtifactDTO):

            if artifact.artifact_type == ArtifactType.XLSX_TESTCASE_DIFF:
                base = "report"
            else:
                base = "diff"

            base_filename = "_".join([
                base,
                artifact.testobject.name,
                artifact.testcase.value,
                artifact.start_ts.strftime(timeformat)
            ])

            if artifact.artifact_type == ArtifactType.JSON_TESTCASE_REPORT:
                file_ending = ".json"
            elif artifact.artifact_type == ArtifactType.TXT_TESTCASE_REPORT:
                file_ending = ".txt"
            elif artifact.artifact_type == ArtifactType.XLSX_TESTCASE_DIFF:
                file_ending = ".xlsx"
            else:
                raise ValueError(f"Unknown artifact type: {artifact.artifact_type}")

            filename = base_filename + file_ending

        else:
            if artifact.artifact_type == ArtifactType.XLSX_TESTRUN_REPORT:
                filename = "testrun_" + artifact.start_ts.strftime(timeformat) + ".xslx"
            else:
                raise ValueError(f"Unknown artifact type: {artifact.artifact_type}")

        return filename
