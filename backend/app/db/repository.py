from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional, Any, Dict
from .models import BaseEntity

class IRepository(ABC):
    
    @abstractmethod
    def get_all(self, entity_type: str) -> List[Dict[str, Any]]:
        pass
        
    @abstractmethod
    def get_by_id(self, entity_type: str, entity_id: str) -> Optional[Dict[str, Any]]:
        pass
        
    @abstractmethod
    def save(self, entity_type: str, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        pass
        
    @abstractmethod
    def delete(self, entity_type: str, entity_id: str) -> bool:
        pass

