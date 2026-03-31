# /tmp/verify_scaling.py
import sys
import os
import pandas as pd
import numpy as np

# Add backend to path
sys.path.append(os.path.abspath('backend'))

from app.feature_engineering.pipeline import generate_feature_dataset
from app.data_loader import load_all_datasets
from app.preference_builder import build_recommendation_params

# 1. Load and Score
mobil, wholesales = load_all_datasets()
df = generate_feature_dataset(mobil, wholesales)

# 2. Check Index Ranges
index_cols = [c for c in df.columns if c.startswith("INDEX_")]
print("\n" + "="*50)
print("INDEX RANGE VERIFICATION (Should be 1-10)")
print("="*50)
for col in index_cols:
    print(f"{col}: Min={df[col].min():.2f}, Max={df[col].max():.2f}, Std={df[col].std():.2f}")

# 3. Simulate Weights for "sporty"
prefs = ["sporty", "enak dikendarai"]
weight_input = {p: 9.0 for p in prefs}
params = build_recommendation_params(prefs, weight_input, [])

print("\n" + "="*50)
print("WEIGHT DICT FOR 'sporty yang enak dikendarai'")
print("="*50)
for k in sorted(params['weight_dict'].keys()):
    print(f"  {k}: {params['weight_dict'][k]}")

# 4. Filter by Budget and see top cars
max_budget = 690e6
filtered = df[df["HARGAOTR"] <= max_budget].copy()

# Run a mini-VIKOR logic check
from vikor.vikor import vikor_rank
ranked = vikor_rank(filtered, params['weight_dict'])

print("\n" + "="*50)
print(f"TOP 5 RECOMMENDATIONS (Max Budget: {max_budget/1e6:.0f}jt)")
print("="*50)
print(ranked[["BRAND", "MODEL", "HARGAOTR", "VIKOR_Q", "INDEX_POWER", "INDEX_HANDLING", "INDEX_PRICE"]].head(5))
