import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_vertical_slice():
    print("--- Testing Phase 3 Vertical Slice (HAB001) ---")
    
    # 1. Check initial state
    print("\n1. Fetching initial Explainability Payload for HAB001...")
    res = requests.get(f"{BASE_URL}/habitations/HAB001/explain")
    if not res.ok:
        print("Failed to fetch initial state:", res.text)
        return
        
    initial_data = res.json()
    print("Initial Overall Risk:", initial_data.get("overall_risk"))
    print("Initial Category:", initial_data.get("risk_category"))
    
    # 2. Trigger recalculation
    print("\n2. Triggering recalculation (Hazard = 95)...")
    res = requests.post(f"{BASE_URL}/simulation/recalculate/HAB001", json={"hazard_score": 95})
    if not res.ok:
        print("Recalculation failed:", res.text)
        return
        
    new_data = res.json()
    print("New Overall Risk:", new_data.get("overall_risk"))
    print("New Category:", new_data.get("risk_category"))
    print("Explanation:", new_data.get("explanation"))
    
    # 3. Check necessity and assignment updates
    print("\n3. Verifying cascading updates on HAB001...")
    res = requests.get(f"{BASE_URL}/habitations/HAB001")
    if not res.ok:
        print("Failed to fetch full hab data:", res.text)
        return
        
    hab_data = res.json()
    print("Necessity Category:", hab_data.get("necessity", {}).get("category"))
    print("Assignments:", json.dumps(hab_data.get("assignments", []), indent=2))
    
    print("\nTest Complete!")

if __name__ == "__main__":
    test_vertical_slice()
