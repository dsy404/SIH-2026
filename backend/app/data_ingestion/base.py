from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class DataProvider(ABC):
    @abstractmethod
    def read_data(self, source: str) -> List[Dict[str, Any]]:
        """Reads data from the source and returns a list of generic dictionaries."""
        pass

    @abstractmethod
    def get_supported_format(self) -> str:
        """Returns the format supported by this provider (e.g., 'csv', 'geojson')."""
        pass

