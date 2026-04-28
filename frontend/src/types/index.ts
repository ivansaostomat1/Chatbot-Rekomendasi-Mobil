// Types for the Car Recommendation Chatbot

export interface CarRecommendation {
  BRAND: string;
  MODEL: string;
  VARIAN: string;
  HARGAOTR?: number;
  CLUSTER_NAME?: string;
  // VIKOR Core
  VIKOR_S?: number;
  VIKOR_R?: number;
  VIKOR_Q?: number;
  VIKOR_STATUS?: string;
  // Compromise validation
  VIKOR_Q1?: number;
  VIKOR_Q2?: number;
  VIKOR_DQ?: number;
  VIKOR_IS_COMPROMISE?: boolean;
  // Criteria index breakdown
  INDEX_POWER?: number;
  INDEX_HANDLING?: number;
  INDEX_EFFICIENCY?: number;
  INDEX_SAFETY?: number;
  INDEX_DRIVER_COMFORT?: number;
  INDEX_PASSENGER_COMFORT?: number;
  INDEX_TECH?: number;
  INDEX_SPACE?: number;
  INDEX_OFFROAD?: number;
  INDEX_LUXURY?: number;
  INDEX_LIFECYCLE_SAFE?: number;
  INDEX_BRAND_STRENGTH?: number;
  INDEX_PRICE?: number;
  INDEX_CLUSTER_MATCH?: number;

  // --- Detail Spesifikasi ---
  BODY_TYPE?: string;
  FUEL?: string;
  CC?: number;
  IS_TURBO?: boolean;
  HORSE_POWER?: number;
  TORQUE?: number;
  TRANSMISSION?: string;
  SEAT?: number;
  GROUND_CLEARANCE?: number;
  LONG?: number;
  WIDTH?: number;
  HEIGHT?: number;
  WHEELBASE?: number;
  EV_RANGE_KM?: number;
  BATTERY?: number;
  POWERTRAIN?: string;
  DRIVE_SYS?: string;
  insight?: string;

  // --- Fitur Brochure / Sales ---
  AIRBAGS?: number;
  ABS?: number;
  EBD?: number;
  ESC?: number;
  TCS?: number;
  AEB?: number;
  ACC?: number;
  LKA?: number;
  RCTA?: number;
  LANE_CENTERING?: number;
  LEVEL_ADAS?: string; 

  APPLE_CARPLAY?: string;
  ANDROID_AUTO?: string;
  WIRELESS_CHARGER?: string;
  SUNROOF?: string;
  POWER_TAILGATE?: string;
  ELECTRIC_SEAT?: string;
  VENTILATED_SEAT?: string;
  MASSAGE_SEAT?: string;
  CAMERA_360?: string;
  HEAD_UP_DISPLAY?: string;
  REAR_SEAT_ENTERTAINMENT?: string;
  LEATHER_SEAT?: string;
  AMBIENT_LIGHT?: string;
  PARKING_BRAKE?: string;
  AUTO_HOLD?: string;
}

export interface ConstraintReport {
  relax_notes?: string[];
  normalized_weights?: Record<string, number>;
  feature_constraints?: {
    passed_constraints?: string[];
    failed_constraints?: string[];
  };
}

export interface ChatRequest {
  preference_terms: string[];
  weight_input: Record<string, number>;
  entities: string[];
  min_budget?: number;
  max_budget?: number;
  top_n: number;
  min_seat?: number;
  min_ground_clearance?: number;
  must_have_sunroof?: boolean;
  must_have_wireless_tech?: boolean;
}

export interface ChatResponse {
  recommendations: CarRecommendation[];
  constraint_report?: ConstraintReport;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  recommendations?: CarRecommendation[];
  constraint_report?: ConstraintReport;
  ask_weights_payload?: Record<string, unknown>;
  timestamp: Date;
  isLoading?: boolean;
}

export interface ClusterInfo {
  name: string;
  count: number;
  percentage: number;
  avgVikoeQ?: number;
  color: string;
}

export interface ClusterEvalData {
  silhouette_score: number;
  n_clusters: number;
  total_cars: number;
  cluster_distribution: ClusterInfo[];
  features_used: string[];
}

export interface RecommendationEvalData {
  sample_recommendations: CarRecommendation[];
  weight_dict: Record<string, number>;
  top_n: number;
  vikor_score_range: { min: number; max: number };
}

export interface NLPEvalData {
  intents: IntentInfo[];
  entities: EntityInfo[];
  model_config: ModelConfig;
}

export interface IntentInfo {
  name: string;
  example_count: number;
  examples: string[];
}

export interface EntityInfo {
  name: string;
  example_count: number;
  examples: string[];
}

export interface ModelConfig {
  pipeline: string[];
  language: string;
  policies: string[];
}

// ── New Evaluation Types ──

export interface NLPMappingTestResult {
  input: string;
  type: string;
  expected: string;
  actual: string;
  correct: boolean;
}

export interface NLPMappingData {
  overall_accuracy: number;
  correct: number;
  total: number;
  per_type_accuracy: Record<string, { accuracy: number; correct: number; total: number }>;
  test_results: NLPMappingTestResult[];
  pipeline_config: {
    language: string;
    pipeline: string[];
    entity_types: string[];
  };
  mapping_tables: {
    preference_index_count: number;
    preference_cluster_count: number;
    need_cluster_count: number;
  };
}

export interface SensitivityScenarioItem {
  rank: number;
  brand: string;
  model: string;
  varian: string;
  VIKOR_Q: number;
  VIKOR_S: number;
  VIKOR_R: number;
  cluster: string;
  INDEX_EFFICIENCY: number;
  INDEX_PERFORMANCE: number;
}

export interface VikorSensitivityData {
  is_sensitive: boolean;
  sensitivity_proof: string;
  scenarios: Record<string, {
    weights_used: Record<string, number> | string;
    top_5: SensitivityScenarioItem[];
  }>;
  formula: {
    Q: string;
    v: number;
    interpretation: string;
  };
}

export interface ClusterProfile {
  count: number;
  avg_features: Record<string, number>;
  top_features: { name: string; value: number }[];
  character_summary: string;
}

export interface ClusterDetailData {
  stability: {
    silhouette_per_k: { k: number; silhouette: number | null }[];
    best_k: { k: number; silhouette: number };
    current_k: number;
    current_silhouette: number;
    interpretation: string;
  };
  semantic_validation: Record<string, ClusterProfile>;
  features_used: string[];
  dendrogram_url?: string;
}

// ── NLP Baseline + Gap Analysis ──

export interface NLPClassMetrics {
  precision: number;
  recall: number;
  f1: number;
  support: number;
  confused_with: Record<string, number>;
}

export interface NLPGap {
  component: string;
  issue: string;
  detail: string;
  severity: 'critical' | 'warning';
  research_opportunity: string;
}

export interface HighConfError {
  text: string;
  true_intent: string;
  predicted: string;
  confidence: number;
}

export interface NLPBaselineData {
  intent: {
    per_class: Record<string, NLPClassMetrics>;
    accuracy: number;
    weighted_f1: number;
    macro_f1: number;
  };
  entity: {
    per_class: Record<string, NLPClassMetrics>;
    accuracy: number;
    weighted_f1: number;
    macro_f1: number;
  };
  errors: {
    intent_errors: { text: string; intent: string; intent_prediction: { name: string; confidence: number } }[];
    entity_errors_count: number;
    high_confidence_errors: HighConfError[];
  };
  gaps: NLPGap[];
  model_config: {
    epochs: number;
    train_split: string;
    test_split: string;
    architecture: string;
    featurizers: string[];
    total_intents: number;
    total_entity_types: number;
  };
}
