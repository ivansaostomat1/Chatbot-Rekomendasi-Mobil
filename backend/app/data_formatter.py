import pandas as pd
import numpy as np

def title_case(text):
    if not text: return text
    return " ".join([w.capitalize() for w in str(text).split()])

def format_car_records(records, transmission_decoding, drivetrain_decoding):
    """
    Shared formatting logic for car records before sending to frontend.
    Handles decoding of numeric features, title casing, and ADAS summary.
    """
    MAP_SUNROOF = {0: "Tidak Ada", 1: "Moonroof", 2: "Panoramic"}
    MAP_CARPLAY = {0: "Tidak Ada", 1: "Kabel (Wired)", 2: "Nirkabel (Wireless)"}
    MAP_AA      = {0: "Tidak Ada", 1: "Kabel (Wired)", 2: "Nirkabel (Wireless)", 3: "Built-in"}
    MAP_JOK     = {0: "Kain (Fabric)", 1: "Bahan Daur Ulang", 2: "Kulit Sintetis (Synthetic)", 3: "Kulit Asli (Leather)", 4: "Kulit Nappa"}
    MAP_BINARY  = {1: "Ada", 0: "Tidak Ada"}

    def decode_feature(val, mapping, default="Tidak Ada"):
        if val is None or pd.isna(val): return default
        try:
            v = float(val)
            return mapping.get(v, default)
        except:
            return str(val)

    for r in records:
        # 1. Renaming Fallbacks (if renaming in engine failed for any reason)
        rename_map = {
            "BODY TYPE": "BODY_TYPE",
            "HORSE POWER (HP)": "HORSE_POWER",
            "TORQUE (Nm)": "TORQUE",
            "GROUND CLEARANCE": "GROUND_CLEARANCE",
            "BATTERY (KWH)": "BATTERY"
        }
        for old_key, new_key in rename_map.items():
            if old_key in r and new_key not in r:
                r[new_key] = r.pop(old_key)

        # 2. Title case Brand, Model, and Body Type for better UI appearance
        r["BRAND"] = title_case(r.get("BRAND"))
        r["MODEL"] = title_case(r.get("MODEL"))
        if r.get("BODY_TYPE"):
            r["BODY_TYPE"] = title_case(r["BODY_TYPE"])
        if r.get("FUEL"):
            r["FUEL"] = title_case(r["FUEL"])
        if r.get("VARIAN"):
            r["VARIAN"] = str(r["VARIAN"]).upper()
        
        # 3. Handle '0' as None for specs where 0 is unrealistic (missing data)
        # except for CC/BATTERY which can be 0 for certain powertrain types
        for spec in ["HORSE_POWER", "TORQUE", "GROUND_CLEARANCE", "LONG", "WIDTH", "HEIGHT", "WHEELBASE"]:
            val = r.get(spec)
            try:
                if val is not None and float(val) <= 0:
                    r[spec] = None
            except:
                pass

        # 4. Decoding of complex features
        r["SUNROOF"] = decode_feature(r.get("SUNROOF"), MAP_SUNROOF)
        r["APPLE_CARPLAY"] = decode_feature(r.get("APPLE_CARPLAY"), MAP_CARPLAY)
        r["ANDROID_AUTO"] = decode_feature(r.get("ANDROID_AUTO"), MAP_AA)
        r["LEATHER_SEAT"] = decode_feature(r.get("LEATHER_SEAT"), MAP_JOK, "Fabric")
        
        # 5. Binary features (Ada / Tidak Ada)
        for feat in ["WIRELESS_CHARGER", "POWER_TAILGATE", "CAMERA_360", "HEAD_UP_DISPLAY", "AMBIENT_LIGHT", "AUTO_HOLD", "REAR_SEAT_ENTERTAINMENT"]:
            if feat in r: r[feat] = decode_feature(r[feat], MAP_BINARY)
            
        r["PARKING_BRAKE"] = decode_feature(r.get("PARKING_BRAKE"), {1: "Elektrik (EPB)", 0: "Manual"}, "Manual")

        # 6. Level ADAS Summary
        adas_score = sum([1 for f in ["AEB", "ACC", "LKA"] if float(r.get(f, 0)) >= 1])
        if adas_score == 3: r["LEVEL_ADAS"] = "Lengkap (Pro)"
        elif adas_score >= 1: r["LEVEL_ADAS"] = "Standar"
        else: r["LEVEL_ADAS"] = "Dasar"

        # 7. Drivetrain & Transmission Decoding
        if r.get("DRIVE_SYS") is not None:
            val = r["DRIVE_SYS"]
            try:
                r["DRIVE_SYS"] = drivetrain_decoding.get(float(val), str(val))
            except:
                pass

        if r.get("TRANSMISSION") is not None:
            val = r["TRANSMISSION"]
            try:
                r["TRANSMISSION"] = transmission_decoding.get(float(val), str(val))
            except:
                pass

        # 8. Final Sanitization of numpy types for JSON
        for key, val in list(r.items()):
            if isinstance(val, (np.floating, np.float64, np.float32)):
                r[key] = float(val)
            elif isinstance(val, (np.integer, np.int64, np.int32)):
                r[key] = int(val)
            elif pd.isna(val):
                r[key] = None

    return records
