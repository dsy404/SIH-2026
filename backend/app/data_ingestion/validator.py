from typing import List, Dict, Any, Tuple

class DataValidator:
    def __init__(self, required_fields: List[str]):
        self.required_fields = required_fields

    def validate(self, data: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Validates the dataset.
        Returns a tuple: (valid_records, invalid_records)
        invalid_records will have an '__errors__' list attached.
        """
        valid = []
        invalid = []

        for idx, record in enumerate(data):
            errors = []
            
            # Check required fields
            for field in self.required_fields:
                if field not in record or record[field] is None or record[field] == "":
                    errors.append(f"Missing required field: {field}")
                    
            # Check coordinates if present
            if 'latitude' in record and 'longitude' in record:
                try:
                    lat = float(record['latitude'])
                    lon = float(record['longitude'])
                    if not (-90 <= lat <= 90):
                        errors.append(f"Invalid latitude: {lat}")
                    if not (-180 <= lon <= 180):
                        errors.append(f"Invalid longitude: {lon}")
                except ValueError:
                    errors.append("Latitude and longitude must be numbers")
                    
            if errors:
                record['__errors__'] = errors
                record['__row_num__'] = idx + 1
                invalid.append(record)
            else:
                valid.append(record)
                
        return valid, invalid
