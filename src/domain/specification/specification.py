from typing import List, Tuple

from src.dtos import (
    TestCaseEntryDTO,
    SpecificationDTO,
    LocationDTO,
    SpecificationType,
    SpecContent,
    SchemaContent,
    RowCountSqlContent,
    CompareSqlContent,
    SchemaSpecificationDTO,
    RowCountSqlDTO,
    CompareSqlDTO,
)
from src.domain.specification.plugins import (
    INamingConventionsFactory,
    ISpecFormatterFactory,
    SpecDeserializationError,
)
from src.infrastructure_ports import (
    IUserStorage,
    StorageError,
)


class SpecificationError(Exception):
    """
    Exception raised when a specification operation fails.
    """


class UnknownSpecificationTypeError(SpecificationError):
    """
    Exception raised when a specification type is unknown
    """


class Specification:
    """
    Core logic for finding, matching, and parsing specifications.
    Uses IUserStorage, INamingConventions, and ISpecFormatterFactory.
    """

    def __init__(
        self,
        user_storage: IUserStorage,
        naming_conventions_factory: INamingConventionsFactory,
        formatter_factory: ISpecFormatterFactory,
    ):
        self.user_storage = user_storage
        self.naming_conventions_factory = naming_conventions_factory
        self.formatter_factory = formatter_factory

    def _find_candidates(
        self,
        location: LocationDTO,
        testcase: TestCaseEntryDTO,
        domain: str,
    ) -> List[Tuple[LocationDTO, List[SpecificationType]]]:
        """
        Find all files in the location that match the naming convention
        """
        naming_conventions = (
            self.naming_conventions_factory.create(domain)
        )
        candidates: List[
            Tuple[LocationDTO, List[SpecificationType]]
        ] = []
        files: List[LocationDTO] = self.user_storage.list_objects(
            location
        )
        for file in files:
            # skip if location is not a file
            if not file.filename:
                continue
            # skip if file does not match the naming convention
            match, matched_spec_types = naming_conventions.match(
                testcase, file
            )
            if not match:
                continue
            candidates.append((file, matched_spec_types))

        return candidates

    def _spec_from_content(
        self,
        content: SpecContent,
        testobject: str,
        location: LocationDTO,
    ) -> SpecificationDTO:
        """
        Create a SpecificationDTO from a SpecContent object.
        """
        result: SpecificationDTO
        if isinstance(content, SchemaContent):
            result = SchemaSpecificationDTO(
                location=location,
                testobject=testobject,
                spec_type=content.spec_type,
                columns=content.columns,
                primary_keys=content.primary_keys,
                partition_columns=content.partition_columns,
                clustering_columns=content.clustering_columns,
            )
        elif isinstance(content, RowCountSqlContent):
            result = RowCountSqlDTO(
                location=location,
                testobject=testobject,
                spec_type=content.spec_type,
                query=content.query,
            )
        elif isinstance(content, CompareSqlContent):
            result = CompareSqlDTO(
                location=location,
                testobject=testobject,
                spec_type=content.spec_type,
                query=content.query,
            )
        else:
            raise UnknownSpecificationTypeError(
                f"Unsupported specification type: "
                f"{content.spec_type}"
            )
        return result

    # rename in list_specs
    def find_specs(
        self,
        location: LocationDTO,
        testcase: TestCaseEntryDTO,
        domain: str,
    ) -> List[SpecificationDTO]:
        """
        Find specification files for a given testcase in the
        provided location.
        """
        results: List[SpecificationDTO] = []
        candidates = self._find_candidates(
            location, testcase, domain
        )

        for file, matched_spec_types in candidates:
            for spec_type in matched_spec_types:
                formatter = self.formatter_factory.get_formatter(
                    spec_type
                )
                try:
                    file_bytes: bytes = self.user_storage.read_object(
                        file
                    )
                    spec_content: SpecContent = (
                        formatter.deserialize(file_bytes)
                    )
                except (StorageError, SpecDeserializationError):
                    # if file can't be read or parsed, silently skip
                    continue
                spec_dto: SpecificationDTO = self._spec_from_content(
                    content=spec_content,
                    testobject=testcase.testobject,
                    location=location,
                )
                results.append(spec_dto)

        return results

    def parse_spec_file(
        self, file: bytes, testobject: str
    ) -> List[SpecificationDTO]:
        """
        Tries parsing a specification file using all available
        formatters and returns all successfully parsed
        SpecificationDTOs.
        """
        results = []
        for spec_type in SpecificationType:
            formatter = self.formatter_factory.get_formatter(
                spec_type
            )
            try:
                spec_content = formatter.deserialize(file)
                spec_dto = self._spec_from_content(
                    content=spec_content,
                    testobject=testobject,
                    location=LocationDTO(
                        path=f"upload://{testobject}_"
                        f"{spec_type.value}.file"
                    ),
                )
                results.append(spec_dto)
            except SpecDeserializationError:
                continue
        return results
