# backend/app/explainer.py

from vikor.vikor import VIKOR_CRITERIA

INDEX_LABELS = {
    "INDEX_POWER": "Tenaga & Performa Mesin",
    "INDEX_HANDLING": "Stabilitas & Kelincahan",
    "INDEX_EFFICIENCY": "Efisiensi BBM",
    "INDEX_SAFETY": "Fitur Keselamatan",
    "INDEX_DRIVER_COMFORT": "Kenyamanan Pengemudi",
    "INDEX_PASSENGER_COMFORT": "Kenyamanan Penumpang",
    "INDEX_TECH": "Teknologi & Fitur Modern",
    "INDEX_SPACE": "Keluasan Kabin",
    "INDEX_OFFROAD": "Kemampuan Offroad/Banjir",
    "INDEX_LUXURY": "Kesan Premium",
    "INDEX_LIFECYCLE_SAFE": "Produk Aman (Trend Wholesale Aktual)",
    "INDEX_BRAND_STRENGTH": "Kekuatan Ekosistem Merek",
    "INDEX_PRICE": "Harga yang Kompetitif",
}

def generate_car_insights(car_record: dict, weight_dict: dict):
    """
    Menghasilkan narasi alasan kenapa mobil ini direkomendasikan.
    Menggunakan data W_DIST_ yang dihasilkan oleh VIKOR.
    """
    def safe_get(d, k, default=0):
        val = d.get(k)
        return float(val) if val is not None else float(default)

    valid_distances = []
    
    # Kriteria kualitas (semua kecuali harga dan match cluster)
    quality_indices = [c for c in VIKOR_CRITERIA if c not in ["INDEX_PRICE", "INDEX_CLUSTER_MATCH"]]
    
    avg_quality = sum([safe_get(car_record, c, 0) for c in quality_indices]) / len(quality_indices)
    price_score = safe_get(car_record, "INDEX_PRICE", 1) # 10 = murah, 1 = mahal
    
    # VFM Index: Semakin tinggi kualitas dan semakin murah harga -> VFM tinggi
    vfm_score = (avg_quality * price_score) / 10
    
    if weight_dict is None: weight_dict = {}

    for crit in VIKOR_CRITERIA:
        w_dist_key = f"W_DIST_{crit}"
        if w_dist_key in car_record:
            user_weight = float(weight_dict.get(crit) or 0)
            if user_weight > 0:
                valid_distances.append({
                    "crit": crit,
                    "w_dist": safe_get(car_record, w_dist_key, 999),
                    "label": INDEX_LABELS.get(crit, crit),
                    "score": safe_get(car_record, crit, 0)
                })

    # Sort berdasarkan jarak terbobot terkecil (performa terbaik relatif terhadap bobot)
    valid_distances.sort(key=lambda x: x["w_dist"])
    top_reasons = valid_distances[:2]
    
    if not top_reasons:
        msg = "Mobil ini secara umum memenuhi kriteria Anda dengan seimbang."
    else:
        insights = []
        for reason in top_reasons:
            insights.append(f"{reason['label']} (Skor {reason['score']}/10)")
        msg = f"Unggul pada {', '.join(insights)}."
    
    # Tambahkan analisa VFM
    if vfm_score > 7:
        msg += " Menawarkan Value for Money yang sangat tinggi di kelasnya."
    elif vfm_score > 5:
        msg += " Memiliki keseimbangan harga dan fitur yang baik."
        
    return msg

def compare_two_cars(car_a: dict, car_b: dict, weight_dict: dict):
    """
    Membandingkan Mobil A (baru/lebih mahal) dengan Mobil B (lama/lebih murah).
    Menghasilkan alasan kenapa A layak dipertimbangkan meskipun lebih mahal.
    """
    def safe_get(d, k, default=0):
        val = d.get(k)
        return float(val) if val is not None else float(default)

    if weight_dict is None: weight_dict = {}

    diffs = []
    for crit in VIKOR_CRITERIA:
        if crit == "INDEX_PRICE": continue
        
        score_a = safe_get(car_a, crit, 0)
        score_b = safe_get(car_b, crit, 0)
        
        if score_a > score_b:
            weight = float(weight_dict.get(crit) or 0.1) # Prioritaskan yang di-bobot user
            diffs.append({
                "crit": crit,
                "label": INDEX_LABELS.get(crit, crit),
                "diff": score_a - score_b,
                "weight": weight,
                "score_a": score_a,
                "score_b": score_b
            })
            
    # Sort berdasarkan (selisih * bobot) untuk menemukan "Value Gain" terbesar
    diffs.sort(key=lambda x: x["diff"] * x["weight"], reverse=True)
    
    if not diffs:
        return f"Meskipun harganya berbeda, {car_a['MODEL']} dan {car_b['MODEL']} memiliki spesifikasi yang sangat mirip."

    top_gain = diffs[0]
    price_diff = car_a['HARGAOTR'] - car_b['HARGAOTR']
    
    msg = f"Dengan menambah budget sekitar {price_diff/1e6:.0f}jt, Anda mendapatkan peningkatan signifikan pada {top_gain['label']} "
    msg += f"({top_gain['score_a']}/10 vs {top_gain['score_b']}/10)."
    
    if len(diffs) > 1:
        next_gain = diffs[1]
        msg += f" Serta fitur {next_gain['label']} yang lebih baik."
        
    return msg
