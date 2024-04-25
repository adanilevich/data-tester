from src.report.ports import SaveReportCommand, ISaveReportCommandHandler, IStorage


class SaveReportCommandHandler(ISaveReportCommandHandler):

    def __init__(self, storage: IStorage):
        self.storage = storage

    def save(self, command: SaveReportCommand):

        location = command.location

        if command.group_by is not None:
            for item in command.group_by:
                if item in command.report.model_fields:
                    location += item + "/"

        if command.report.format is None:
            raise ValueError("Report must be formatted and the applied format specified.")

        self.storage.save(
            content=command.report.content,
            format=command.report.format,
            location=location
        )
