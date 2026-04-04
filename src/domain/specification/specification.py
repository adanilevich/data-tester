from typing import List, Tuple

from src.dtos import (
    TestCaseEntryDTO,
    SpecDTO,
    LocationDTO,
    SpecType,
    spec_class_by_type,
    Importance,
    NotificationDTO,
    NotificationProcess,
)
from src.domain.specification.plugins import INamingConventionsFactory, ISpecParserFactory
from src.infrastructure_ports import (
    IUserStorage,
    INotifier,
    StorageError,
)


class SpecificationError(Exception):
    """
    Exception raised when a specification operation fails.
    """


class UnknownSpecTypeError(SpecificationError):
    """
    Exception raised when a specification type is unknown
    """


class Specification:
    """
    Core logic for finding, matching, and parsing specifications.
    """

    def __init__(
        self,
        user_storage: IUserStorage,
        naming_conventions_factory: INamingConventionsFactory,
        parser_factory: ISpecParserFactory,
        notifiers: List[INotifier] | None = None,
    ):
        self.user_storage = user_storage
        self.naming_conventions_factory = naming_conventions_factory
        self.parser_factory = parser_factory
        self.notifiers: List[INotifier] = notifiers or []

    def _notify(
        self,
        message: str,
        domain: str = "",
        importance: Importance = Importance.INFO,
    ):
        notification = NotificationDTO(
            domain=domain,
            process=NotificationProcess.SPECIFICATION,
            importance=importance,
            message=message,
        )
        for notifier in self.notifiers:
            notifier.notify(notification)

    def find_candidates(
        self,
        location: LocationDTO,
        testcase: TestCaseEntryDTO,
    ) -> List[Tuple[LocationDTO, List[SpecType]]]:
        """
        Find all files in the location that match the naming convention
        """
        naming_conventions = self.naming_conventions_factory.create(testcase.domain)
        candidates: List[Tuple[LocationDTO, List[SpecType]]] = []
        files: List[LocationDTO] = self.user_storage.list_objects(location)
        for file in files:
            if not file.filename:  # skip if location is not a file
                continue
            match, matched_spec_types = naming_conventions.match(testcase, file)
            if match:
                candidates.append((file, matched_spec_types))

        return candidates

    def list_specs(self, loc: LocationDTO, testcase: TestCaseEntryDTO) -> List[SpecDTO]:
        """
        Find specification files for a given testcase in the
        provided location.
        """
        results: List[SpecDTO] = []
        candidates = self.find_candidates(loc, testcase)

        for file, spec_types in candidates:
            for spec_type in spec_types:
                spec_class = spec_class_by_type(spec_type)
                spec = spec_class(location=loc, testobject=testcase.testobject)
                parser = self.parser_factory.get_parser(testcase.domain, spec_type)
                try:
                    file_bytes: bytes = self.user_storage.read_object(file)
                    spec = parser.parse(file_bytes, spec)
                except StorageError:  # parser errors are handled by parser
                    spec.message="Couldn't read file from storage"
                    self._notify(
                        f"Failed to read spec file: {file.path}",
                        domain=testcase.domain,
                        importance=Importance.WARNING,
                    )
                results.append(spec)

        self._notify(
            f"Found {len(results)} spec(s) for"
            f" {testcase.testobject} in {loc.path}",
            domain=testcase.domain,
        )
        return results
