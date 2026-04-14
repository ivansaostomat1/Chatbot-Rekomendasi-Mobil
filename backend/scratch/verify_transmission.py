import os
import sys

# Path setup
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.abspath(os.path.join(current_dir, ".."))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from vikor.ranking_engine import recommend_cars

def test_decoding():
    print("Testing Transmission Decoding...")
    
    # Test case 1: ICE Car (should be AT/MT/CVT/DCT)
    print("\nCase 1: ICE Car (Expect AT/MT/CVT/DCT)")
    result = recommend_cars(
        preference_terms=["keluarga"],
        top_n=3,
        max_budget=500_000_000
    )
    
    for car in result['recommendations']:
        print(f"Model: {car['MODEL']}, Varian: {car['VARIAN']}, Transmission: {car['TRANSMISSION']}")

    # Test case 2: EV Car (should be Single Speed)
    print("\nCase 2: EV Car (Expect Single Speed)")
    result_ev = recommend_cars(
        powertrain="LISTRIK",
        top_n=3
    )
    
    for car in result_ev['recommendations']:
        print(f"Model: {car['MODEL']}, Varian: {car['VARIAN']}, Transmission: {car['TRANSMISSION']}")

if __name__ == "__main__":
    test_decoding()
