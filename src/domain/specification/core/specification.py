from typing import List
import itertools

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
    IRequirements,
)
from src.infrastructure.storage import IStorageFactory


class Specification:
    """
    Core logic for finding, matching, and parsing specifications.
    Uses IStorage, INamingConventions, and a list of IFormatter.
    """

    def __init__(
        self,
        storage_factory: IStorageFactory,
        naming_conventions_factory: INamingConventionsFactory,
        formatter_factory: ISpecFormatterFactory,
        requirements: IRequirements,
    ):
        self.storage_factory = storage_factory
        self.naming_conventions_factory = naming_conventions_factory
        self.formatter_factory = formatter_factory
        self.requirements = requirements

    def _find_candidates(
        self, location: LocationDTO, testcase: TestCaseEntryDTO, domain: str
    ) -> List[LocationDTO]:
        """
        Find all files in the location that match the naming convention
        """
        naming_conventions = self.naming_conventions_factory.create(domain)
        candidates: List[LocationDTO] = []
        storage = self.storage_factory.get_storage(location)
        files: List[LocationDTO] = storage.list_files(location)
        for file in files:
            # skip if location is not a file
            if not file.filename:
                continue
            # skip if file does not match the naming convention
            if not naming_conventions.match(testcase, file):
                continue
            candidates.append(file)

        return candidates

    def _spec_from_content(
        self, content: SpecContent, testobject: str, location: LocationDTO
    ) -> SpecificationDTO:
        """
        Create a SpecificationDTO from a SpecContent object, testobject name and location.
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
            raise ValueError(f"Unsupported specification type: {content.spec_type}")
        return result

    def find_specs(
        self, location: LocationDTO, testcase: TestCaseEntryDTO, domain: str
    ) -> List[SpecificationDTO]:
        """
        Find specification files for a given testcase in the provided location
        """
        results: List[SpecificationDTO] = []
        # Find all files in the location that match the naming convention
        candidates = self._find_candidates(location, testcase, domain)
        required_specs = self.requirements.get_requirements(testcase)

        # for each candidate file, try to parse it with all required spec types
        for file, spec_type in itertools.product(candidates, required_specs):
            formatter = self.formatter_factory.get_formatter(spec_type)
            try:
                storage = self.storage_factory.get_storage(file)
                file_bytes = storage.read_bytes(file)
                spec_content = formatter.deserialize(file_bytes)
            # if parsing or reading fails, try next spec type
            except Exception:
                continue

            spec_dto = self._spec_from_content(
                content=spec_content,
                testobject=testcase.testobject,
                location=location,
            )
            results.append(spec_dto)

        return results

    def parse_spec_file(self, file: bytes, testobject: str) -> List[SpecificationDTO]:
        """
        Tries parsing a specification file using all available formatters
        and returns all successfully parsed SpecificationDTOs.
        """
        results = []
        for spec_type in SpecificationType:
            formatter = self.formatter_factory.get_formatter(spec_type)
            try:
                spec_content = formatter.deserialize(file)
                spec_dto = self._spec_from_content(
                    content=spec_content,
                    testobject=testobject,
                    location=LocationDTO(
                        path=f"upload://{testobject}_{spec_type.value}.file"
                    ),
                )
                results.append(spec_dto)
            # if parsing or reading fails, try next spec type
            except Exception:
                continue
        return results
