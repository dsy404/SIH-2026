from __future__ import annotations
from typing import List, Dict, Any
from .base import DataProvider

class RasterProvider(DataProvider):
    def read_data(self, source: str) -> List[Dict[str, Any]]:
        # Stub for Raster parsing (requires rasterio)
        raise NotImplementedError("Raster/DEM parsing is planned for future architecture.")

    def get_supported_format(self) -> str:
        return "raster"

