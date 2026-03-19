# chatbot-rekomendasi-mobil/backend/app/schemas.py

from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any


# ======================================================
# SINGLE CAR RESULT
# ======================================================

class CarRecommendation(BaseModel):

    BRAND: str
    MODEL: str
    VARIAN: str

    HARGAOTR: Optional[int]
    CLUSTER_NAME: Optional[str]

    VIKOR_Q: Optional[float] = None
    VIKOR_S: Optional[float] = None
    VIKOR_R: Optional[float] = None
    VIKOR_Q1: Optional[float] = None
    VIKOR_Q2: Optional[float] = None
    VIKOR_DQ: Optional[float] = None
    VIKOR_IS_COMPROMISE: Optional[bool] = None
    VIKOR_STATUS: Optional[str] = None
    INDEX_PRICE: Optional[float] = None

    model_config = {
        "from_attributes": True
    }


# ======================================================
# RESPONSE SCHEMA
# ======================================================

class RecommendationResponse(BaseModel):

    recommendations: List[CarRecommendation]


# ======================================================
# CHAT REQUEST (FROM NLP)
# ======================================================

class ChatRequest(BaseModel):

    user_message: Optional[str] = None

    preference_terms: List[str] = Field(default_factory=list)

    need_terms: List[str] = Field(default_factory=list)

    weight_input: Dict[str, float] = Field(default_factory=dict)

    entities: List[str] = Field(default_factory=list)

    min_budget: Optional[int] = None
    max_budget: Optional[int] = None

    top_n: int = Field(default=5, ge=1, le=20)

    min_seat: Optional[int] = None
    min_ground_clearance: Optional[float] = None
    must_have_sunroof: Optional[bool] = False
    must_have_wireless_tech: Optional[bool] = False

    manual_weights: Optional[Dict[str, float]] = None


# ======================================================
# DIRECT RECOMMENDATION REQUEST (OPTIONAL)
# ======================================================

class RecommendationRequest(BaseModel):

    weight_dict: Optional[Dict[str, float]] = Field(default_factory=dict)
    brand: Optional[str] = None
    cluster_name: Optional[str] = None

    max_budget: Optional[int] = None
    min_budget: Optional[int] = None

    top_n: int = Field(default=5, ge=1, le=20)

    body_type: Optional[str] = None
    powertrain: Optional[str] = None

    feature_constraints: Optional[Dict[str, int]] = Field(default_factory=dict)

    min_seat: Optional[int] = None
    min_ground_clearance: Optional[float] = None
    must_have_sunroof: Optional[bool] = False
    must_have_wireless_tech: Optional[bool] = False


# ======================================================
# HISTORY SCHEMA
# ======================================================

class HistoryItemResponse(BaseModel):
    id: int
    user_message: str
    timestamp: str
    
    # NLP
    nlp_preferences: List[str]
    nlp_needs: List[str]
    nlp_entities: List[str]
    
    # Clustering
    cluster_name: Optional[str]
    hard_filters_applied: Dict[str, Any]  # misal {"min_seat": 6}
    
    # Weights
    weight_dict_used: Dict[str, float] = {}
    
    # VIKOR & Constraints
    cars_total: int
    cars_after_constraint: int
    top_recommendations: List[CarRecommendation]

    model_config = {
        "from_attributes": True
    }