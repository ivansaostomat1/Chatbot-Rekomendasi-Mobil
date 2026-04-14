"""Quick check - call /docs or /openapi.json to verify schema"""
import requests
import json

# Cek schema yang aktif di server
r = requests.get("http://localhost:8000/openapi.json")
schema = r.json()

# Cari definition untuk RecommendationResponse
definitions = schema.get("components", {}).get("schemas", {})
rec_response = definitions.get("RecommendationResponse", {})
print("RecommendationResponse schema dari server yang berjalan:")
print(json.dumps(rec_response, indent=2))
