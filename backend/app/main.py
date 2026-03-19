# chatbot-rekomendasi-mobil/backend/app/main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any

    
from .schemas import (
    RecommendationRequest,
    RecommendationResponse,
    CarRecommendation
)

from vikor.ranking_engine import recommend_cars
from .schemas import ChatRequest, HistoryItemResponse
from .preference_builder import build_recommendation_params
from .database import init_db, save_chat_history, get_recent_history, delete_chat_history
from contextlib import asynccontextmanager

# ======================================================
# FASTAPI APP INITIALIZATION
# ======================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup database at startup
    init_db()
    yield

app = FastAPI(
    title="Car Recommendation API",
    description="API sistem rekomendasi mobil menggunakan Clustering + VIKOR",
    version="1.0.0",
    lifespan=lifespan
)


# ======================================================
# CORS (UNTUK FLUTTER / WEB CLIENT)
# ======================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # bisa diganti domain tertentu nanti
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ======================================================
# HEALTH CHECK
# ======================================================

@app.get("/")
def root():
    return {"message": "Car Recommendation API is running"}


# ======================================================
# MAIN RECOMMENDATION ENDPOINT
# ======================================================

@app.post("/recommend", response_model=RecommendationResponse)
def recommend(request: RecommendationRequest):
    request_data = request.dict()
    try:

        results = recommend_cars(
            **request_data
        )

        recommendations = [
            CarRecommendation(**car) for car in results
        ]

        return RecommendationResponse(
            recommendations=recommendations
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Recommendation engine error: {str(e)}"
        )


# ======================================================
# CHAT ENDPOINT (NLP BRIDGE)
# ======================================================

@app.post("/chat", response_model=RecommendationResponse)
def chat(request: ChatRequest):

    print("==================================================")
    print(f"[FASTAPI] Endpoint /chat terpanggil!")
    print(f"[FASTAPI] Data Request: {request.dict()}")

    try:
        from app.feature_ontology import NEED_CLUSTER_MAP, NEED_HARD_FILTER_MAP

        print("[FASTAPI] Membangun parameter rekomendasi...")
        params = build_recommendation_params(
            preference_terms=request.preference_terms,
            weight_input=request.weight_input,
            entities=request.entities,
        )
        # ──────────────────────────────────────────────────────
        # SINGLE SOURCE OF TRUTH: user manual_weights → VIKOR
        # NLP weight_input hanya dipakai kalau user tidak atur manual
        # ──────────────────────────────────────────────────────
        if request.manual_weights:
            print(f"[FASTAPI] ✅ PURE USER-DRIVEN: Menggunakan manual_weights dari frontend: {request.manual_weights}")
            params["weight_dict"] = request.manual_weights

        params["min_budget"] = request.min_budget
        params["max_budget"] = request.max_budget
        params.update({
            "min_seat": request.min_seat,
            "min_ground_clearance": request.min_ground_clearance,
            "must_have_sunroof": request.must_have_sunroof,
            "must_have_wireless_tech": request.must_have_wireless_tech
        })

        # ======================================================
        # PROSES NEED_TERMS → CLUSTER + HARD FILTERS
        # need_terms yang punya cluster jelas (keluarga, offroad, dll.)
        # di-map ke cluster_name dan hard filter yang tepat.
        # Ini mengoverride cluster yang mungkin sudah ditemukan dari preference_terms.
        # ======================================================

        need_terms = request.need_terms or []
        print(f"[FASTAPI] Processing need_terms: {need_terms}")

        for need in need_terms:
            need_lower = need.lower().strip()

            # Map need → cluster (override preference-based cluster)
            if need_lower in NEED_CLUSTER_MAP:
                params["cluster_name"] = NEED_CLUSTER_MAP[need_lower]
                print(f"[FASTAPI] Cluster dari need '{need_lower}': {params['cluster_name']}")

            # Map need → hard filters (kemudian merge, prioritaskan yang lebih besar)
            if need_lower in NEED_HARD_FILTER_MAP:
                for filter_key, filter_val in NEED_HARD_FILTER_MAP[need_lower].items():
                    current = params.get(filter_key)
                    if current is None or filter_val > current:
                        params[filter_key] = filter_val
                        print(f"[FASTAPI] Hard filter dari need '{need_lower}': {filter_key}={filter_val}")

        print(f"[FASTAPI] Parameter hasil build: {params}")
        print("[FASTAPI] Memanggil VIKOR Ranking Engine (recommend_cars)...")

        results = recommend_cars(
            **params,
            top_n=request.top_n
        )
        
        # Ekstrak data dari dictionary return recommend_cars
        recommendations_data = results.get("recommendations", [])
        constraint_report = results.get("constraint_report", {})
        
        print(f"[FASTAPI] Selesai Ranking! Mendapatkan {len(recommendations_data)} mobil.")

        recommendations = [
            CarRecommendation(**car)
            for car in recommendations_data
        ]

        print("[FASTAPI] Mengembalikan response ke RASA.")
        
        # Simpan History secara Sinkron
        try:
            save_chat_history(
                user_message=request.user_message or "",
                nlp_preferences=request.preference_terms,
                nlp_needs=request.need_terms,
                nlp_entities=request.entities,
                cluster_name=params.get("cluster_name"),
                hard_filters_applied={
                    "min_seat": params.get("min_seat"),
                    "min_ground_clearance": params.get("min_ground_clearance"),
                    "min_budget": params.get("min_budget"),
                    "max_budget": params.get("max_budget"),
                    "must_have_sunroof": params.get("must_have_sunroof"),
                    "must_have_wireless_tech": params.get("must_have_wireless_tech")
                },
                cars_total=612,
                cars_after_constraint=constraint_report.get("hard_filters", {}).get("remaining_cars", 0),
                top_recommendations=recommendations_data,
                weight_dict_used=constraint_report.get("normalized_weights", {})
            )
            print("[FASTAPI] ✅ Berhasil menyimpan History Evaluasi ke DB.")
        except Exception as e:
            print(f"[FASTAPI] ⚠️ Gagal menyimpan History Evaluasi: {e}")

        print("==================================================")

        return RecommendationResponse(
            recommendations=recommendations
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Chat recommendation error: {str(e)}"
        )

@app.get("/features")
def feature_summary():
    from vikor.ranking_engine import get_feature_summary
    return get_feature_summary()

@app.get("/history", response_model=List[HistoryItemResponse])
def get_chat_history():
    """Mengembalikan history evaluasi chatbot"""
    try:
        data = get_recent_history(limit=20)
        return data
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Mendapatkan history error: {str(e)}"
        )


@app.delete("/history/{history_id}")
def delete_history(history_id: int):
    """Menghapus record history tertentu."""
    try:
        delete_chat_history(history_id)
        return {"status": "success", "message": f"History ID {history_id} dihapus."}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gagal menghapus history: {str(e)}"
        )


# ======================================================
# EVALUATION ENDPOINTS
# ======================================================

@app.get("/evaluasi/clustering")
def eval_clustering():
    """Return clustering evaluation metrics."""
    try:
        from vikor.ranking_engine import DF_CARS
        from clustering.agglomerative import build_feature_matrix, CLUSTER_FEATURES
        from sklearn.metrics import silhouette_score

        df = DF_CARS.copy()
        X, features_used = build_feature_matrix(df)

        labels = df["CLUSTER_ID"].values
        score = float(silhouette_score(X, labels))

        cluster_counts = df["CLUSTER_NAME"].value_counts().to_dict()
        total = len(df)

        CLUSTER_COLORS = {
            "City Car": "#00BB77",
            "Family Car": "#00A693",
            "Offroad": "#1E6FD9",
            "Performance": "#F59E0B",
            "Luxury": "#8B5CF6",
        }

        distribution = [
            {
                "name": name,
                "count": count,
                "percentage": round(count / total * 100, 1),
                "color": CLUSTER_COLORS.get(name, "#00A693")
            }
            for name, count in cluster_counts.items()
        ]

        return {
            "silhouette_score": score,
            "n_clusters": int(df["CLUSTER_ID"].nunique()),
            "total_cars": total,
            "cluster_distribution": distribution,
            "features_used": features_used
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/evaluasi/rekomendasi")
def eval_rekomendasi():
    """Return a sample VIKOR ranking for evaluation visualization."""
    try:
        default_weights = {
            "efficiency": 0.30,
            "performance": 0.20,
            "safety": 0.25,
            "tech": 0.15,
            "comfort": 0.10,
        }
        results = recommend_cars(weight_dict=default_weights, top_n=5)
        from vikor.ranking_engine import DF_CARS
        vikor_vals = DF_CARS["VIKOR_Q"].dropna() if "VIKOR_Q" in DF_CARS.columns else None
        return {
            "sample_recommendations": results,
            "weight_dict": default_weights,
            "top_n": 5,
            "vikor_score_range": {
                "min": float(vikor_vals.min()) if vikor_vals is not None else 0.0,
                "max": float(vikor_vals.max()) if vikor_vals is not None else 1.0,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ======================================================
# NLP MAPPING ACCURACY EVALUATION
# ======================================================

@app.get("/evaluasi/nlp/mapping")
def eval_nlp_mapping():
    """
    Evaluate NLP → Decision Mapping Accuracy.
    Tests: preference→INDEX, preference→Cluster, need→Cluster
    """
    try:
        from app.feature_ontology import (
            PREFERENCE_INDEX_MAP,
            PREFERENCE_CLUSTER_MAP,
            NEED_CLUSTER_MAP
        )

        # --- Test dataset for mapping accuracy ---
        test_cases = [
            # preference → INDEX mapping
            {"input": "irit", "type": "preference_index", "expected": "INDEX_EFFICIENCY"},
            {"input": "hemat", "type": "preference_index", "expected": "INDEX_EFFICIENCY"},
            {"input": "kencang", "type": "preference_index", "expected": "INDEX_PERFORMANCE"},
            {"input": "nyaman", "type": "preference_index", "expected": "INDEX_PASSENGER_COMFORT"},
            {"input": "aman", "type": "preference_index", "expected": "INDEX_SAFETY"},
            {"input": "teknologi", "type": "preference_index", "expected": "INDEX_TECH"},
            {"input": "mewah", "type": "preference_index", "expected": "INDEX_LUXURY"},
            {"input": "banjir", "type": "preference_index", "expected": "INDEX_OFFROAD"},
            {"input": "sporty", "type": "preference_index", "expected": "INDEX_FUN_TO_DRIVE"},
            {"input": "luas", "type": "preference_index", "expected": "INDEX_SPACE"},
            {"input": "canggih", "type": "preference_index", "expected": "INDEX_TECH"},
            {"input": "ngebut", "type": "preference_index", "expected": "INDEX_FUN_TO_DRIVE"},
            # preference → Cluster mapping
            {"input": "irit", "type": "preference_cluster", "expected": "City Car"},
            {"input": "keluarga", "type": "preference_cluster", "expected": "Family Car"},
            {"input": "kencang", "type": "preference_cluster", "expected": "Performance"},
            {"input": "banjir", "type": "preference_cluster", "expected": "Offroad"},
            {"input": "mewah", "type": "preference_cluster", "expected": "Luxury"},
            {"input": "sporty", "type": "preference_cluster", "expected": "Performance"},
            {"input": "hemat", "type": "preference_cluster", "expected": "City Car"},
            {"input": "luas", "type": "preference_cluster", "expected": "Family Car"},
            # need → Cluster mapping
            {"input": "keluarga", "type": "need_cluster", "expected": "Family Car"},
            {"input": "keluarga besar", "type": "need_cluster", "expected": "Family Car"},
            {"input": "offroad", "type": "need_cluster", "expected": "Offroad"},
            {"input": "banjir", "type": "need_cluster", "expected": "Offroad"},
            {"input": "mewah", "type": "need_cluster", "expected": "Luxury"},
            {"input": "mudik", "type": "need_cluster", "expected": "Family Car"},
        ]

        results = []
        correct = 0
        total = len(test_cases)

        # Per-type tracking
        type_stats = {}

        for tc in test_cases:
            t = tc["type"]
            inp = tc["input"]
            expected = tc["expected"]

            if t == "preference_index":
                actual = PREFERENCE_INDEX_MAP.get(inp, None)
            elif t == "preference_cluster":
                actual = PREFERENCE_CLUSTER_MAP.get(inp, None)
            elif t == "need_cluster":
                actual = NEED_CLUSTER_MAP.get(inp, None)
            else:
                actual = None

            is_correct = actual == expected
            if is_correct:
                correct += 1

            if t not in type_stats:
                type_stats[t] = {"correct": 0, "total": 0}
            type_stats[t]["total"] += 1
            if is_correct:
                type_stats[t]["correct"] += 1

            results.append({
                "input": inp,
                "type": t,
                "expected": expected,
                "actual": actual or "NOT_FOUND",
                "correct": is_correct
            })

        # Per-type accuracy
        per_type_accuracy = {}
        for t, stats in type_stats.items():
            acc = stats["correct"] / stats["total"] if stats["total"] > 0 else 0
            per_type_accuracy[t] = {
                "accuracy": round(acc, 4),
                "correct": stats["correct"],
                "total": stats["total"]
            }

        return {
            "overall_accuracy": round(correct / total, 4) if total > 0 else 0,
            "correct": correct,
            "total": total,
            "per_type_accuracy": per_type_accuracy,
            "test_results": results,
            "pipeline_config": {
                "language": "id",
                "pipeline": [
                    "WhitespaceTokenizer",
                    "RegexFeaturizer",
                    "LexicalSyntacticFeaturizer",
                    "CountVectorsFeaturizer (word)",
                    "CountVectorsFeaturizer (char_wb, 3-5 ngram)",
                    "DIETClassifier (200 epochs)",
                    "EntitySynonymMapper"
                ],
                "entity_types": ["preference", "budget", "brand", "body_type", "powertrain", "feature", "hard_filter", "need"]
            },
            "mapping_tables": {
                "preference_index_count": len(PREFERENCE_INDEX_MAP),
                "preference_cluster_count": len(PREFERENCE_CLUSTER_MAP),
                "need_cluster_count": len(NEED_CLUSTER_MAP),
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ======================================================
# VIKOR SENSITIVITY ANALYSIS
# ======================================================

@app.get("/evaluasi/vikor/sensitivity")
def eval_vikor_sensitivity():
    """
    Run VIKOR with 3 different weight scenarios to prove sensitivity.
    Scenario A: Efficiency heavy
    Scenario B: Performance heavy
    Scenario C: Equal weights
    """
    try:
        scenarios = {
            "A_efficiency_heavy": {
                "INDEX_EFFICIENCY": 0.6,
                "INDEX_PERFORMANCE": 0.05,
                "INDEX_SAFETY": 0.1,
                "INDEX_TECH": 0.05,
                "INDEX_PASSENGER_COMFORT": 0.05,
                "INDEX_SPACE": 0.05,
                "INDEX_PRICE": 0.1,
            },
            "B_performance_heavy": {
                "INDEX_PERFORMANCE": 0.5,
                "INDEX_FUN_TO_DRIVE": 0.15,
                "INDEX_EFFICIENCY": 0.05,
                "INDEX_SAFETY": 0.1,
                "INDEX_TECH": 0.05,
                "INDEX_PASSENGER_COMFORT": 0.05,
                "INDEX_SPACE": 0.05,
                "INDEX_PRICE": 0.05,
            },
            "C_equal_weights": {}  # empty = equal weights
        }

        scenario_results = {}
        for name, weights in scenarios.items():
            result = recommend_cars(weight_dict=weights, top_n=5)
            recs = result.get("recommendations", [])
            scenario_results[name] = {
                "weights_used": weights if weights else "equal (auto)",
                "top_5": [
                    {
                        "rank": i + 1,
                        "brand": r.get("BRAND", ""),
                        "model": r.get("MODEL", ""),
                        "varian": r.get("VARIAN", ""),
                        "VIKOR_Q": round(r.get("VIKOR_Q", 0), 4),
                        "VIKOR_S": round(r.get("VIKOR_S", 0), 4),
                        "VIKOR_R": round(r.get("VIKOR_R", 0), 4),
                        "cluster": r.get("CLUSTER_NAME", ""),
                        "INDEX_EFFICIENCY": round(r.get("INDEX_EFFICIENCY", 0), 3),
                        "INDEX_PERFORMANCE": round(r.get("INDEX_PERFORMANCE", 0), 3),
                    }
                    for i, r in enumerate(recs[:5])
                ]
            }

        # Check if rankings differ between scenarios
        rankings = {}
        for name, data in scenario_results.items():
            rankings[name] = [f"{r['brand']} {r['model']}" for r in data["top_5"]]

        is_sensitive = not (rankings.get("A_efficiency_heavy") == rankings.get("B_performance_heavy"))

        return {
            "is_sensitive": is_sensitive,
            "sensitivity_proof": "Ranking berubah sesuai bobot preferensi → sistem terbukti sensitif." if is_sensitive else "Ranking sama untuk semua skenario → perlu cek data.",
            "scenarios": scenario_results,
            "formula": {
                "Q": "Q = v(S - S*) / (S⁻ - S*) + (1-v)(R - R*) / (R⁻ - R*)",
                "v": 0.5,
                "interpretation": "Semakin kecil Q → semakin optimal. Perubahan weight → ∂Q/∂w menghasilkan ranking berbeda."
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ======================================================
# CLUSTERING DETAILED EVALUATION (STABILITY + SEMANTIC)
# ======================================================

@app.get("/evaluasi/clustering/detail")
def eval_clustering_detail():
    """
    Detailed clustering evaluation:
    1. Stability: silhouette for k=3..7
    2. Semantic: avg INDEX values per cluster (proves cluster meaning)
    """
    try:
        from vikor.ranking_engine import DF_CARS
        from clustering.agglomerative import build_feature_matrix, CLUSTER_FEATURES
        from sklearn.cluster import AgglomerativeClustering
        from sklearn.metrics import silhouette_score
        import numpy as np

        df = DF_CARS.copy()
        X, features_used = build_feature_matrix(df)

        # 1. Stability: silhouette per k
        stability = []
        for k in range(3, 8):
            try:
                model = AgglomerativeClustering(n_clusters=k, linkage="ward")
                labels = model.fit_predict(X)
                score = float(silhouette_score(X, labels))
                stability.append({"k": k, "silhouette": round(score, 4)})
            except Exception:
                stability.append({"k": k, "silhouette": None})

        best_k = max(stability, key=lambda x: x["silhouette"] or 0)

        # 2. Semantic: avg feature per cluster
        features = [c for c in CLUSTER_FEATURES if c in df.columns]
        cluster_profiles = {}
        for cname in df["CLUSTER_NAME"].unique():
            sub = df[df["CLUSTER_NAME"] == cname]
            profile = {}
            for f in features:
                profile[f] = round(float(sub[f].mean()), 4)
            # Find top-3 strongest features
            sorted_feats = sorted(profile.items(), key=lambda x: x[1], reverse=True)
            cluster_profiles[cname] = {
                "count": int(len(sub)),
                "avg_features": profile,
                "top_features": [{"name": f, "value": v} for f, v in sorted_feats[:3]],
                "character_summary": " + ".join([f.replace("INDEX_", "") for f, _ in sorted_feats[:3]])
            }

        # Silhouette interpretation
        current_silhouette = float(silhouette_score(X, df["CLUSTER_ID"].values))
        if current_silhouette > 0.5:
            interpretation = "Bagus — cluster terbentuk jelas & terpisah."
        elif current_silhouette > 0.2:
            interpretation = "Cukup — struktur cluster moderat."
        else:
            interpretation = "Lemah — cluster kurang terpisah."

        return {
            "stability": {
                "silhouette_per_k": stability,
                "best_k": best_k,
                "current_k": 5,
                "current_silhouette": round(current_silhouette, 4),
                "interpretation": interpretation,
            },
            "semantic_validation": cluster_profiles,
            "features_used": features_used,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))