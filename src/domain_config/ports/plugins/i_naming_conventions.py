from abc import ABC, abstractmethod

class INamingConventions(ABC):
    @abstractmethod
    def match(self, name: str) -> bool:
        """
        Check if given object name, e.g. filename, matches naming conventions
        defined for domain_config files
        """