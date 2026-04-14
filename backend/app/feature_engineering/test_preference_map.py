# test_preference_map.py
# Jalankan: python test_preference_map.py
# Untuk verifikasi bahwa mapping sudah meng-cover kasus-kasus yang sebelumnya gagal

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from preference_weight_map import build_ui_state, resolve_preference_weights

BOLD  = "\033[1m"
GREEN = "\033[92m"
RED   = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def check(label, prefs, expected_high=None, expected_cluster=None):
    """
    expected_high: list kriteria yang harus --- 7
    expected_cluster: string nama cluster
    """
    result = build_ui_state(prefs)
    weights = result["base_weight_profile"]
    cluster = result["cluster_name"]

    passed = True
    issues = []

    if expected_high:
        for crit in expected_high:
            if weights.get(crit, 0) < 7:
                passed = False
                issues.append(f"{crit}={weights.get(crit, '?')} (harusnya ---7)")

    if expected_cluster and cluster != expected_cluster:
        passed = False
        issues.append(f"cluster='{cluster}' (harusnya '{expected_cluster}')")

    status = f"{GREEN}PASS{RESET}" if passed else f"{RED}FAIL{RESET}"
    print(f"\n{BOLD}[{status}] {label}{RESET}")
    print(f"  Input     : {prefs}")
    print(f"  Cluster   : {cluster}")
    print(f"  Weights   : ", end="")

    # Print hanya yang non-default (tidak = 5.0)
    non_default = {k: v for k, v in weights.items() if v != 5.0}
    if non_default:
        print(non_default)
    else:
        print("(semua default=5)")

    if issues:
        print(f"  {RED}Issues    : {issues}{RESET}")

    return passed


if __name__ == "__main__":
    print("=" * 60)
    print("PREFERENCE WEIGHT MAP --- TEST SUITE")
    print("=" * 60)

    results = []

    # --------- KASUS YANG SEBELUMNYA GAGAL (dari screenshot) ------------------------------------------------------------------

    results.append(check(
        label="[GAGAL SEBELUMNYA] 'irit dan nyaman untuk harian'",
        prefs=["irit", "nyaman", "harian"],
        expected_high=["efficiency", "driver_comfort", "price"],
    ))

    results.append(check(
        label="[GAGAL SEBELUMNYA] 'yang irit dan nyaman untuk harian bisa'",
        prefs=["irit", "nyaman", "harian", "bisa"],
        expected_high=["efficiency", "driver_comfort"],
    ))

    # --------- STOPWORDS HARUS DI-FILTER ------------------------------------------------------------------------------------------------------------------------------

    results.append(check(
        label="[STOPWORD] 'sedang' harus di-ignore",
        prefs=["sedang"],
        expected_high=[],   # Tidak ada yang naik
    ))

    results.append(check(
        label="[STOPWORD] 'saya sedang cari' harus semua default",
        prefs=["saya", "sedang", "cari"],
    ))

    # --------- SINGLE PREFERENCE ------------------------------------------------------------------------------------------------------------------------------------------------------

    results.append(check(
        label="Single: 'irit'",
        prefs=["irit"],
        expected_high=["efficiency"],
    ))

    results.append(check(
        label="Single: 'kencang'",
        prefs=["kencang"],
        expected_high=["power"],
    ))

    results.append(check(
        label="Single: 'nyaman'",
        prefs=["nyaman"],
        expected_high=["driver_comfort", "passenger_comfort"],
    ))

    results.append(check(
        label="Single: 'tangguh'",
        prefs=["tangguh"],
        expected_high=["offroad"],
    ))

    results.append(check(
        label="Single: 'keluarga'",
        prefs=["keluarga"],
        expected_high=["space", "passenger_comfort"],
        expected_cluster="Family Car",
    ))

    # --------- MULTI PREFERENCE ---------------------------------------------------------------------------------------------------------------------------------------------------------

    results.append(check(
        label="Multi: 'irit' + 'nyaman'",
        prefs=["irit", "nyaman"],
        expected_high=["efficiency", "driver_comfort", "passenger_comfort"],
    ))

    results.append(check(
        label="Multi: 'irit' + 'nyaman' + 'canggih'",
        prefs=["irit", "nyaman", "canggih"],
        expected_high=["efficiency", "driver_comfort", "tech"],
    ))

    results.append(check(
        label="Multi: 'kencang' + 'irit' (paradoks)",
        prefs=["kencang", "irit"],
        expected_high=["power", "efficiency"],
    ))

    results.append(check(
        label="Multi: 'sporty' + 'anak muda'",
        prefs=["sporty", "anak muda"],
        expected_high=["handling", "tech"],
        expected_cluster="Sport & Performa",
    ))

    results.append(check(
        label="Multi: 'lincah' + 'gesit' + 'harian'",
        prefs=["lincah", "gesit", "harian"],
        expected_high=["handling", "efficiency"],
    ))

    results.append(check(
        label="Multi: 'nyaman' + 'keluarga' + 'perjalanan jauh'",
        prefs=["nyaman", "keluarga", "perjalanan jauh"],
        expected_high=["passenger_comfort", "space", "driver_comfort"],
        expected_cluster="Family Car",
    ))

    results.append(check(
        label="Multi: 'aman' + 'nyaman' + 'bebas banjir'",
        prefs=["aman", "nyaman", "bebas banjir"],
        expected_high=["safety", "driver_comfort", "offroad"],
    ))

    results.append(check(
        label="Multi: 'mewah' + 'canggih'",
        prefs=["mewah", "canggih"],
        expected_high=["luxury", "tech"],
        expected_cluster="Luxury & Premium",
    ))

    # --------- SUMMARY ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    total = len(results)
    passed = sum(results)
    print("\n" + "=" * 60)
    print(f"HASIL: {passed}/{total} test passed")
    if passed == total:
        print(f"{GREEN}Semua test PASS ---{RESET}")
    else:
        print(f"{RED}{total-passed} test GAGAL --- --- cek mapping di preference_weight_map.py{RESET}")
    print("=" * 60)

