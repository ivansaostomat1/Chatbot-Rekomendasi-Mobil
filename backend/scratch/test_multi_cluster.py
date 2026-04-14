import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.feature_engineering.preference_weight_map import detect_cluster_from_weights

def test_clustering():
    print("Testing Multi-Cluster Logic...")
    
    # Test 1: Family Needs
    weights_family = {'space': 9, 'passenger_comfort': 8, 'efficiency': 5}
    res1 = detect_cluster_from_weights(weights_family)
    print(f"Family Case: {res1} (Expected: ['Family Car'])")
    
    # Test 2: Eco + Family
    weights_mixed = {'space': 9, 'passenger_comfort': 8, 'efficiency': 9}
    res2 = detect_cluster_from_weights(weights_mixed)
    print(f"Mixed Case (Eco+Family): {res2} (Expected both 'Family Car' and 'City Car' in list)")

    # Test 3: Global
    weights_global = {'space': 5, 'efficiency': 5}
    res3 = detect_cluster_from_weights(weights_global)
    print(f"Global Case: {res3} (Expected: ['Global'])")

if __name__ == "__main__":
    test_clustering()
