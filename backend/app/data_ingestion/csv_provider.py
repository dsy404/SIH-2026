from __future__ import annotations
from typing import List, Dict, Any
from .base import DataProvider
import csv
import io

class CSVProvider(DataProvider):
    def read_data(self, source: str) -> List[Dict[str, Any]]:
        # Source would be file content (CSV string)
        try:
            f = io.StringIO(source)
            reader = csv.DictReader(f)
            parsed_data = []
            for row in reader:
                # Convert string types to appropriate Python types if needed
                parsed_data.append(dict(row))
            return parsed_data
        except Exception as e:
            raise ValueError(f"Failed to parse CSV: {str(e)}")

    def get_supported_format(self) -> str:
        return "csv"

