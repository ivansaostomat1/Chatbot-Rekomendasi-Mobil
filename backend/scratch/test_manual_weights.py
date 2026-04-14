
import requests
import json

URL = "http://localhost:8001/chat"

def test_manual_weights():
    # Simulate a request from the frontend after manual weighting
    payload = {
        "user_message": "cari mobil keluarga",
        "preference_terms": ["keluarga"],
        "manual_weights": {
            "INDEX_POWER": 8.0,
            "INDEX_EFFICIENCY": 10.0,
            "INDEX_SPACE": 10.0,
            "INDEX_SAFETY": 9.0
        },
        "entities": ["keluarga"],
        "top_n": 5
    }

    print(f"Testing manual weights request to {URL}...")
    try:
        response = requests.post(URL, json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Successfully received recommendations!")
            print(f"Full JSON Keys: {list(data.keys())}")
            print(f"Count: {len(data.get('recommendations', []))}")
            print(f"Constraint Report: {data.get('constraint_report')}")
        else:
            print(f"Error Response: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_manual_weights()
