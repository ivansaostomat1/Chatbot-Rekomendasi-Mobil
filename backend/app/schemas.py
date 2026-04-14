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
    DRIVE_SYS: Optional[str] = None
    POWERTRAIN: Optional[str] = None
    
    # --- Detail Spesifikasi Tambahan ---
    BODY_TYPE: Optional[str] = Field(None, alias="BODY TYPE")
    FUEL: Optional[str] = None
    CC: Optional[float] = None
    HORSE_POWER: Optional[float] = Field(None, alias="HORSE POWER (HP)")
    TORQUE: Optional[float] = Field(None, alias="TORQUE (Nm)")
    TRANSMISSION: Optional[str] = None
    SEAT: Optional[int] = None
    GROUND_CLEARANCE: Optional[float] = Field(None, alias="GROUND CLEARANCE")
    LONG: Optional[float] = None
    WIDTH: Optional[float] = None
    HEIGHT: Optional[float] = None
    WHEELBASE: Optional[float] = None
    EV_RANGE_KM: Optional[float] = None
    BATTERY: Optional[float] = Field(None, alias="BATTERY (KWH)")
    
    # --- Fitur Brochure / Sales ---
    # Keselamatan & ADAS
    AIRBAGS: Optional[int] = None
    ABS: Optional[float] = None
    EBD: Optional[float] = None
    ESC: Optional[float] = None
    TCS: Optional[float] = None
    AEB: Optional[float] = None
    ACC: Optional[float] = None
    LKA: Optional[float] = None
    RCTA: Optional[float] = None
    LANE_CENTERING: Optional[float] = None
    LEVEL_ADAS: Optional[str] = None # Derived in backend
    
    # Tech & Comfort
    APPLE_CARPLAY: Optional[str] = None
    ANDROID_AUTO: Optional[str] = None
    WIRELESS_CHARGER: Optional[str] = None
    SUNROOF: Optional[str] = None
    POWER_TAILGATE: Optional[str] = None
    ELECTRIC_SEAT: Optional[str] = None
    VENTILATED_SEAT: Optional[str] = None
    MASSAGE_SEAT: Optional[str] = None
    CAMERA_360: Optional[str] = None
    HEAD_UP_DISPLAY: Optional[str] = None
    REAR_SEAT_ENTERTAINMENT: Optional[str] = None
    LEATHER_SEAT: Optional[str] = None
    AMBIENT_LIGHT: Optional[str] = None
    PARKING_BRAKE: Optional[str] = None
    AUTO_HOLD: Optional[str] = None
    
    insight: Optional[str] = None

    class Config:
        allow_population_by_field_name = True
        orm_mode = True


# ======================================================
# RESPONSE SCHEMA
# ======================================================

class RecommendationResponse(BaseModel):

    recommendations: List[CarRecommendation]
    constraint_report: Optional[Dict[str, Any]] = None
    comparison_insight: Optional[str] = None


# ======================================================
# CHAT REQUEST (FROM NLP)
# ======================================================

class ChatRequest(BaseModel):

    user_message: Optional[str] = None

    preference_terms: List[str] = Field(default_factory=list)

    need_terms: List[str] = Field(default_factory=list)

    weight_input: Dict[str, float] = Field(default_factory=dict)

    entities: List[str] = Field(default_factory=list)
    negated_terms: List[str] = Field(default_factory=list)
    raw_budgets: List[str] = Field(default_factory=list)

    min_budget: Optional[int] = None
    max_budget: Optional[int] = None
    previous_max_budget: Optional[int] = None

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
    drive_sys: Optional[str] = None

    feature_constraints: Optional[Dict[str, int]] = Field(default_factory=dict)
    negated_terms: List[str] = Field(default_factory=list)

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

    class Config:
        orm_mode = True