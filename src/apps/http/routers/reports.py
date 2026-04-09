from uuid import UUID

from fastapi import APIRouter
from fastapi.responses import Response

from src.apps.http.di import ReportDriverDep
from src.dtos import ReportArtifact, ReportArtifactFormat

router = APIRouter(tags=["reports"])

_MEDIA_TYPES = {
    ReportArtifactFormat.TXT: "text/plain; charset=utf-8",
    ReportArtifactFormat.XLSX: (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ),
}


@router.get("/{domain}/testcase/{testcase_id}/artifact")
def get_testcase_artifact(
    domain: str,
    testcase_id: UUID,
    driver: ReportDriverDep,
    artifact: ReportArtifact = ReportArtifact.REPORT,
    format: ReportArtifactFormat = ReportArtifactFormat.TXT,
) -> Response:
    content = driver.create_testcase_report_artifact(
        testcase_id=testcase_id,
        artifact=artifact,
        artifact_format=format,
    )
    ext = format.value
    return Response(
        content=content,
        media_type=_MEDIA_TYPES[format],
        headers={
            "Content-Disposition": f"attachment; filename={testcase_id}.{ext}"
        },
    )


@router.get("/{domain}/testrun/{testrun_id}/artifact")
def get_testrun_artifact(
    domain: str,
    testrun_id: UUID,
    driver: ReportDriverDep,
    format: ReportArtifactFormat = ReportArtifactFormat.XLSX,
) -> Response:
    content = driver.create_testrun_report_artifact(
        testrun_id=testrun_id,
        artifact_format=format,
    )
    ext = format.value
    return Response(
        content=content,
        media_type=_MEDIA_TYPES[format],
        headers={
            "Content-Disposition": f"attachment; filename={testrun_id}.{ext}"
        },
    )
