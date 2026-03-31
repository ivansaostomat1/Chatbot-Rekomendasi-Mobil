# /tmp/simulate_nlp.py
import sys
import os
import numpy as np

# Add backend to path
sys.path.append(os.path.abspath('backend'))

from app.preference_builder import build_recommendation_params
from app.feature_ontology import PREFERENCE_INDEX_MAP

# Simulate what ActionRecommendCar does
def mock_rasa_logic(text, preference_terms):
    weight_input = {}
    for p in preference_terms:
        weight_input[p] = 9.0 # Assume boost_score 9
    
    params = build_recommendation_params(
        preference_terms=preference_terms,
        weight_input=weight_input,
        entities=[]
    )
    return params

# Test Prompt
text = "cari mobil sporty yang enak dikendarai"
prefs = ["sporty", "enak dikendarai"]

params = mock_rasa_logic(text, prefs)

print(f"Prompt: {text}")
print(f"Preferences: {prefs}")
print("-" * 30)
print("Computed Weights (weight_dict):")
# Sort keys for consistent output
for k in sorted(params['weight_dict'].keys()):
    print(f"  {k}: {params['weight_dict'][k]}")

print("-" * 30)
print(f"Detected Cluster: {params['cluster_name']}")
