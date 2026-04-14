"""
Debug script: Send EXACT payload yang dikirim frontend ke /chat endpoint
untuk menemukan error yang sebenarnya terjadi di server yang sedang berjalan.
"""
import requests
import json
import sys

# Target port 8000 (server yang sedang berjalan, bukan 8001 temporary)
URL = "http://localhost:8000/chat"

# Simulasi EXACT payload dari frontend submitWeights
# Ini adalah format yang dikirim oleh Rasa via actions.py
payload_from_rasa = {
    "user_message": "cari mobil irit untuk keluarga",
    "preference_terms": ["keluarga", "irit"],
    "need_terms": [],
    "weight_input": {},
    "entities": [],
    "negated_terms": [],
    "raw_budgets": [],
    "min_budget": None,
    "max_budget": None,
    "previous_max_budget": None,
    "top_n": 5,
    "min_seat": None,
    "min_ground_clearance": None,
    "must_have_sunroof": False,
    "must_have_wireless_tech": False,
    # Manual weights dengan kunci INDEX_ persis seperti CRITERIA_MAP di frontend
    "manual_weights": {
        "INDEX_POWER": 3.0,
        "INDEX_HANDLING": 2.0,
        "INDEX_EFFICIENCY": 9.0,
        "INDEX_DRIVER_COMFORT": 7.0,
        "INDEX_PASSENGER_COMFORT": 8.0,
        "INDEX_SAFETY": 8.0,
        "INDEX_TECH": 5.0,
        "INDEX_SPACE": 9.0,
        "INDEX_OFFROAD": 1.0,
        "INDEX_LUXURY": 2.0,
        "INDEX_LIFECYCLE_SAFE": 5.0,
        "INDEX_BRAND_STRENGTH": 5.0,
        "INDEX_PRICE": 10.0
    },
    "cluster_name": "Family Comfort",
    "cluster_display_name": "Keluarga & Nyaman",
    "base_weight_profile": {}
}

print(f"[TEST] Sending to {URL}")
print(f"[TEST] Payload:\n{json.dumps(payload_from_rasa, indent=2)}")
print("=" * 60)

try:
    response = requests.post(URL, json=payload_from_rasa, timeout=30)
    print(f"[TEST] Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"[TEST] SUCCESS!")
        print(f"[TEST] Keys returned: {list(data.keys())}")
        print(f"[TEST] Recommendations count: {len(data.get('recommendations', []))}")
        print(f"[TEST] Constraint Report: {data.get('constraint_report')}")
        if data.get('recommendations'):
            print(f"[TEST] First car: {data['recommendations'][0].get('MODEL')}")
    else:
        print(f"[TEST] ERROR: {response.status_code}")
        try:
            print(f"[TEST] Error detail: {response.json()}")
        except:
            print(f"[TEST] Raw response: {response.text[:500]}")

except requests.exceptions.ConnectionError:
    print("[TEST] KONEKSI GAGAL - Server di port 8000 tidak berjalan!")
    print("[TEST] Pastikan FastAPI backend sudah dijalankan terlebih dahulu.")
except Exception as e:
    print(f"[TEST] Exception: {type(e).__name__}: {e}")
