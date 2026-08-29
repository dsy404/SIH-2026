from __future__ import annotations
from typing import List, Dict, Any
from .base import DataProvider

class ShapefileProvider(DataProvider):
    def read_data(self, source: str) -> List[Dict[str, Any]]:
        # Stub for Shapefile parsing (requires geopandas/fiona)
        raise NotImplementedError("Shapefile parsing is planned for future architecture.")

    def get_supported_format(self) -> str:
        return "shapefile"

