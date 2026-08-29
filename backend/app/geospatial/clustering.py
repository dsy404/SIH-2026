from typing import List, Dict, Any
import numpy as np
from sklearn.cluster import DBSCAN

def find_clusters(data: List[Dict[str, Any]], epsilon_km: float = 2.0, min_samples: int = 2) -> List[Dict[str, Any]]:
    """
    Groups habitations into clusters based on spatial proximity using DBSCAN.
    epsilon_km specifies the maximum distance between two samples for one to be considered as in the neighborhood of the other.
    """
    if not data or len(data) < min_samples:
        for record in data:
            record['cluster_id'] = -1
        return data

    # Extract coordinates (lat, lon) in radians for haversine metric
    coords = []
    valid_indices = []
    
    for idx, record in enumerate(data):
        if 'latitude' in record and 'longitude' in record:
            coords.append([np.radians(float(record['latitude'])), np.radians(float(record['longitude']))])
            valid_indices.append(idx)
            
    if not coords:
        for record in data:
            record['cluster_id'] = -1
        return data

    coords = np.array(coords)
    
    # Earth radius in km
    kms_per_radian = 6371.0088
    epsilon = epsilon_km / kms_per_radian
    
    db = DBSCAN(eps=epsilon, min_samples=min_samples, algorithm='ball_tree', metric='haversine').fit(coords)
    labels = db.labels_
    
    # Assign cluster IDs back to data
    for i, idx in enumerate(valid_indices):
        data[idx]['cluster_id'] = int(labels[i])
        
    # For any data that didn't have coordinates
    for idx, record in enumerate(data):
        if 'cluster_id' not in record:
            record['cluster_id'] = -1
            
    return data
