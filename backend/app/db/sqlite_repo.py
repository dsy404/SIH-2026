import sqlite3
import json
from typing import List, Dict, Any, Optional
from .repository import IRepository

class SQLiteRepository(IRepository):
    def __init__(self, db_path: str = "disaster_relocation.db"):
        self.db_path = db_path
        self._init_db()
        
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
        
    def _init_db(self):
        # We use a simple JSON document store approach for MVP to avoid complex migrations
        # entity_type table holds all records for that type as JSON
        pass
        
    def get_all(self, entity_type: str) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        # Initialize table if not exists
        conn.execute(f"CREATE TABLE IF NOT EXISTS {entity_type} (id TEXT PRIMARY KEY, data TEXT)")
        cursor = conn.execute(f"SELECT data FROM {entity_type}")
        results = [json.loads(row['data']) for row in cursor.fetchall()]
        conn.close()
        return results
        
    def get_by_id(self, entity_type: str, entity_id: str) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        conn.execute(f"CREATE TABLE IF NOT EXISTS {entity_type} (id TEXT PRIMARY KEY, data TEXT)")
        cursor = conn.execute(f"SELECT data FROM {entity_type} WHERE id = ?", (entity_id,))
        row = cursor.fetchone()
        conn.close()
        return json.loads(row['data']) if row else None
        
    def save(self, entity_type: str, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        conn = self._get_connection()
        conn.execute(f"CREATE TABLE IF NOT EXISTS {entity_type} (id TEXT PRIMARY KEY, data TEXT)")
        entity_id = entity_data.get('id')
        if not entity_id:
            raise ValueError("Entity must have an 'id'")
            
        data_str = json.dumps(entity_data)
        conn.execute(f"INSERT OR REPLACE INTO {entity_type} (id, data) VALUES (?, ?)", (entity_id, data_str))
        conn.commit()
        conn.close()
        return entity_data
        
    def delete(self, entity_type: str, entity_id: str) -> bool:
        conn = self._get_connection()
        conn.execute(f"CREATE TABLE IF NOT EXISTS {entity_type} (id TEXT PRIMARY KEY, data TEXT)")
        cursor = conn.execute(f"DELETE FROM {entity_type} WHERE id = ?", (entity_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted
