from src.report.ports import SaveReportCommand, ISaveReportCommandHandler, IStorage
from src.report import Report


class SaveReportCommandHandler(ISaveReportCommandHandler):

    def __init__(self, storage: IStorage):

        self.storage: IStorage = storage

    def save(self, command: SaveReportCommand):

        Report.save_artifacts(
            artifacts=list(command.report.artifacts.values()),
            location=command.location,
            tags=command.tags,
            save_only_artifact_content=command.save_only_artifact_content,
            storage=self.storage,
        )
