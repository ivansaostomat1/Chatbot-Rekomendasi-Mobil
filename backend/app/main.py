# chatbot-rekomendasi-mobil/backend/app/main.py

import os
import sys

# Path injection for app package
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.abspath(os.path.join(current_dir, ".."))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any

    
from .schemas import (
    RecommendationRequest,
    RecommendationResponse,
    CarRecommendation
)

from vikor.ranking_engine import recommend_cars, FEATURE_SUMMARY
from .schemas import ChatRequest
from .preference_builder import (
    build_recommendation_params, 
    UI_TO_INDEX_MAP
)
from .feature_engineering.preference_weight_map import build_ui_state
from .database import init_db, save_chat_history
from .explainer import generate_car_insights, compare_two_cars
from contextlib import asynccontextmanager
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

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
    description="API sistem rekomendasi mobil menggunakan VIKOR dan K-Means",
    version="1.0.0",
    lifespan=lifespan
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    print(f"OMGGG VALIDATION ERROR: {exc.errors()}")
    print(f"OMGGG REQUEST BODY: {exc.body}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body},
    )

# ======================================================
# STATIC FILES (RASA RESULTS)
# ======================================================
import os
from fastapi.staticfiles import StaticFiles

# Mount Rasa results directory to serve images like confusion matrix
results_path = os.path.join(os.path.dirname(__file__), "..", "rasa", "results")
if os.path.exists(results_path):
    app.mount("/rasa-results", StaticFiles(directory=results_path), name="rasa-results")



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

@app.post("/recommend", response_model=RecommendationResponse, response_model_by_alias=False)
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
# K-MEANS & DISAMBIGUATE LOGIC NOW IN /chat
# ======================================================


# ======================================================
# CHAT ENDPOINT (NLP BRIDGE)
# ======================================================

# (Logic moved to /chat)

@app.post("/chat")
def chat(request: ChatRequest):

    print("==================================================")
    print(f"[FASTAPI] Endpoint /chat terpanggil!")
    print(f"[FASTAPI] Data Request: {request.dict()}")

    try:
        # 1. K-MEANS ROUTE (Tanpa VIKOR)
        if request.target_car:
            from app.feature_engineering.clustering import clustering_engine
            # Cek apakah exact match atau perlu disambiguasi
            matches = clustering_engine.search_car_models(request.target_car)
            if not matches:
                return {"error": f"Mobil {request.target_car} tidak ditemukan."}
            if len(matches) > 1:
                return {"action": "disambiguate_car", "matches": matches, "query": request.target_car}
                
            # Exact Match -> Lookalike
            exact = matches[0]
            results = clustering_engine.find_similar_cars(
                brand=exact["brand"],
                model=exact["model"],
                varian=exact["varian"],
                top_n=5
            )
            if "error" in results:
                return {"error": results["error"]}
                
            recommendations = []
            for car in results["recommendations"]:
                try:
                    recommendations.append(CarRecommendation(**car).dict())
                except Exception as ve:
                    print(f"[FASTAPI] [ERROR] Validation failed for car {car.get('BRAND')} {car.get('MODEL')}: {ve}")
                    # Lanjutkan agar tidak crash total
            
            return {
                "recommendations": recommendations,
                "constraint_report": {"relax_notes": ["K-Means clustering mode active"]}
            }

        # 2. VIKOR ROUTE (Perankingan Kriteria)
        from app.feature_ontology import NEED_HARD_FILTER_MAP
        from app.query_guard import parse_budget_strings
        from .feature_engineering.preference_weight_map import build_ui_state

        # A. Cek apakah ini panggilan pertama dari NLU (belum ada manual_weights)
        if not request.manual_weights:
            all_prefs = request.preference_terms + request.need_terms
            ui_state = build_ui_state(
                preference_terms=all_prefs,
                entity_terms=request.entities
            )
            # Kembalikan instruksi ke frontend untuk memunculkan slider bobot
            payload = request.dict()
            payload.update(ui_state)
            return {"action": "ask_weights", "payload": payload}

        # B. Panggilan kedua dari Frontend (sudah ada manual_weights)
        print("[FASTAPI] Membangun parameter rekomendasi...")
        params = build_recommendation_params(
            preference_terms=request.preference_terms,
            weight_input=request.weight_input,
            entities=request.entities,
        )

        # ------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # SINGLE SOURCE OF TRUTH: user manual_weights --- VIKOR
        # ------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # BRIDGE: Map Internal Keys -> UI Keys (INDEX_...)
        # ------------------------------------------------------------------------------------------------------------------------------------------------------------------
        from .preference_builder import UI_TO_INDEX_MAP
        if request.manual_weights:
            # Map frontend short keys to internal INDEX_ keys 
            mapped_weights = {
                UI_TO_INDEX_MAP.get(k, k): v 
                for k, v in request.manual_weights.items()
            }
            # FORCE: 'Value For Money' (Price) must always be 10.0 as per user requirement
            mapped_weights["INDEX_PRICE"] = 10.0
            
            print(f"[FASTAPI] [USER-DRIVEN] Menggunakan manual_weights (mapped): {mapped_weights}")
            params["weight_dict"] = mapped_weights

        # Parse budget if raw_budgets exist, else fallback to min/max_budget
        parsed_min, parsed_max = parse_budget_strings(request.raw_budgets)
        
        params["min_budget"] = request.min_budget if request.min_budget is not None else parsed_min
        params["max_budget"] = request.max_budget if request.max_budget is not None else parsed_max
        
        params.update({
            "min_seat": request.min_seat,
            "min_ground_clearance": request.min_ground_clearance,
            "must_have_sunroof": request.must_have_sunroof,
            "must_have_wireless_tech": request.must_have_wireless_tech
        })

        # ======================================================
        # PROSES NEED_TERMS --- HARD FILTERS
        # ======================================================

        need_terms = request.need_terms or []
        print(f"[FASTAPI] Processing need_terms: {need_terms}")

        for need in need_terms:
            need_lower = need.lower().strip()

            # Map need --- hard filters (kemudian merge, prioritaskan yang lebih besar)
            if need_lower in NEED_HARD_FILTER_MAP:
                for filter_key, filter_val in NEED_HARD_FILTER_MAP[need_lower].items():
                    current = params.get(filter_key)
                    if current is None or filter_val > current:
                        params[filter_key] = filter_val
                        print(f"[FASTAPI] Hard filter dari need '{need_lower}': {filter_key}={filter_val}")

        # Terapkan negated_terms (Hard Exclusion) --- mobil yang harus dibuang dari dataset
        if request.negated_terms:
            params["negated_terms"] = request.negated_terms
            print(f"[FASTAPI] [NEGATION] Negated Terms (Exclusion Aktif): {request.negated_terms}")

        # Terapkan drive_sys (AWD/RWD/FWD) dari entitas
        if params.get("drive_sys"):
            print(f"[FASTAPI] [DRIVE] Drive System filter aktif: {params['drive_sys']}")

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

        # ======================================================
        # COMPATIVE INSIGHT (OPTIONAL)
        # ======================================================
        comparison_insight = None
        if request.previous_max_budget and request.max_budget and request.max_budget > request.previous_max_budget:
            print(f"[FASTAPI] [STATS] Running Comparison Analysis (+{request.max_budget - request.previous_max_budget}jt)")
            
            # 1. Run base recommendation (original budget)
            base_params = params.copy()
            base_params["max_budget"] = request.previous_max_budget
            base_results = recommend_cars(**base_params, top_n=1)
            
            if base_results.get("recommendations") and recommendations_data:
                base_top = base_results["recommendations"][0]
                new_top = recommendations_data[0]
                
                if base_top["MODEL"] != new_top["MODEL"]:
                    from .explainer import compare_two_cars # Import inside to avoid circular check if any
                    comparison_insight = compare_two_cars(new_top, base_top, params.get("weight_dict", {}))

        # ======================================================
        # GENERATE INDIVIDUAL CAR INSIGHTS
        # ======================================================
        for car in recommendations_data:
            car["insight"] = generate_car_insights(car, params.get("weight_dict", {}))

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
                cluster_name="Personalized",
                hard_filters_applied=params, 
                cars_total=FEATURE_SUMMARY.get("total_cars", 0) if FEATURE_SUMMARY else 612,
                cars_after_constraint=constraint_report.get("budget", {}).get("remaining_cars", 0),
                top_recommendations=[car.dict() for car in recommendations],
                weight_dict_used=params.get("weight_dict"),
                session_id=request.session_id
            )
            print("[FASTAPI] [SUCCESS] Berhasil menyimpan History Evaluasi ke DB.")

        except Exception as e:
            print(f"[FASTAPI] [ERROR] Gagal menyimpan History Evaluasi: {e}")

        print(f"[FASTAPI] Final constraint_report keys: {constraint_report.keys() if constraint_report else 'None'}")
        
        print("==================================================")

        return RecommendationResponse(
            recommendations=recommendations,
            constraint_report=constraint_report,
            comparison_insight=comparison_insight
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Chat recommendation error: {str(e)}"
        )

@app.get("/features")
def feature_summary():
    from vikor.ranking_engine import get_feature_summary
    return get_feature_summary()

@app.get("/katalog")
def get_katalog():
    from .data_loader import load_all_datasets
    import pandas as pd
    import numpy as np

    try:
        mobil, wholesales, retail = load_all_datasets()
        
        months = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']

        # 1. Wholesales: per-varian level (has BRAND, MODEL, VARIAN, TOTAL_2025)
        if 'TOTAL_2025' in wholesales.columns:
            ws_subset = wholesales[['BRAND', 'MODEL', 'VARIAN', 'TOTAL_2025']].copy()
            ws_subset.rename(columns={'TOTAL_2025': 'WHOLESALES_VARIAN'}, inplace=True)
        else:
            for m in months:
                if m not in wholesales.columns:
                    wholesales[m] = 0
            wholesales['WHOLESALES_VARIAN'] = wholesales[months].sum(axis=1)
            ws_subset = wholesales[['BRAND', 'MODEL', 'VARIAN', 'WHOLESALES_VARIAN']].copy()

        # 2. Retail: brand-level only (has BRAND, JAN-DEC)
        for m in months:
            if m not in retail.columns:
                retail[m] = 0
        retail['RETAIL_BRAND'] = retail[months].sum(axis=1)
        rt_subset = retail[['BRAND', 'RETAIL_BRAND']].copy()

        # 3. Merge mobil ← wholesales (per varian)
        katalog = pd.merge(mobil, ws_subset, on=['BRAND', 'MODEL', 'VARIAN'], how='left')

        # 4. Merge katalog ← retail (per brand)
        katalog = pd.merge(katalog, rt_subset, on='BRAND', how='left')

        # Fill NaN sales with 0
        katalog['WHOLESALES_VARIAN'] = katalog['WHOLESALES_VARIAN'].fillna(0).astype(int)
        katalog['RETAIL_BRAND'] = katalog['RETAIL_BRAND'].fillna(0).astype(int)
        
        # Replace remaining NaN with None for JSON serialization
        katalog = katalog.replace({np.nan: None})
        
        return katalog.to_dict(orient='records')
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error loading catalog data: {str(e)}"
        )


