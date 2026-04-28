# UML Diagram — Chatbot Rekomendasi Mobil

## 1. Use Case Diagram

```mermaid
graph LR
    subgraph System["Sistem Chatbot Rekomendasi Mobil"]
        UC1["UC-1: Memulai Percakapan"]
        UC2["UC-2: Meminta Rekomendasi Mobil"]
        UC3["UC-3: Memilih / Memperbaiki Preferensi"]
        UC4["UC-4: Membandingkan Budget"]
        UC5["UC-5: Mengatur Bobot Kriteria Manual"]
        UC6["UC-6: Melihat Riwayat Pencarian"]
    end

    User(("👤 User"))

    User --> UC1
    User --> UC2
    User --> UC3
    User --> UC4
    User --> UC5
    User --> UC6

    UC2 -.->|include| UC_NLU["Proses NLU (Intent & Entity)"]
    UC2 -.->|include| UC_Cluster["Clustering HAC"]
    UC2 -.->|include| UC_VIKOR["Perankingan VIKOR"]
    UC3 -.->|extend| UC2
    UC4 -.->|extend| UC2
    UC5 -.->|extend| UC2
```

### Deskripsi Use Case

| UC | Nama | Aktor | Deskripsi |
|----|------|-------|-----------|
| UC-1 | Memulai Percakapan | User | User menyapa chatbot, sistem membalas sapaan |
| UC-2 | Meminta Rekomendasi Mobil | User | User menyebutkan budget/kebutuhan, sistem memproses NLU → Clustering → VIKOR dan menampilkan Top-N rekomendasi |
| UC-3 | Memilih/Memperbaiki Preferensi | User | User menyempurnakan kriteria pencarian (preferensi, fitur, powertrain) pada sesi yang sama |
| UC-4 | Membandingkan Budget | User | User meminta perbandingan hasil rekomendasi dengan budget yang dinaikkan |
| UC-5 | Mengatur Bobot Kriteria Manual | User | User mengatur slider bobot (Performa, Irit, Kenyamanan, dll.) di UI frontend |
| UC-6 | Melihat Riwayat Pencarian | User | User melihat atau menghapus riwayat evaluasi pencarian sebelumnya |

---

## 2. Activity Diagram

### 2.1 Activity Diagram — UC-1: Memulai Percakapan

```mermaid
flowchart TD
    A([Start]) --> B["User mengirim pesan sapaan"]
    B --> C{"Rasa NLU mendeteksi intent"}
    C -->|"intent = greet"| D["Rasa menjalankan utter_greet"]
    C -->|"intent lain"| E["Rasa menjalankan utter_default"]
    D --> F["Chatbot menampilkan pesan sambutan"]
    E --> G["Chatbot menampilkan pesan fallback"]
    F --> H([End])
    G --> H
```

### 2.2 Activity Diagram — UC-2: Meminta Rekomendasi Mobil

```mermaid
flowchart TD
    A([Start]) --> B["User mengirim pesan berisi budget & kebutuhan"]
    B --> C["Rasa NLU: Klasifikasi Intent & Ekstraksi Entity"]
    C --> D["ActionRecommendCar: extract_entities()"]
    D --> E["DialogueContextManager: merge context"]
    E --> F{"Ada budget?"}
    F -->|Tidak| G["Chatbot meminta budget (utter_ask_budget)"]
    G --> H([End])
    F -->|Ya| I{"Ada preferensi?"}
    I -->|Tidak| J["Chatbot meminta preferensi (utter_ask_initial_preference)"]
    J --> H
    I -->|Ya| K["Kirim payload ke FastAPI /chat"]
    K --> L["PreferenceBuilder: build_recommendation_params()"]
    L --> M["Tentukan Cluster via HAC Profiling"]
    M --> N["Apply Query Guard & Hard Filters"]
    N --> O["Apply Budget Filter"]
    O --> P{"Dataset kosong?"}
    P -->|Ya| Q["Relaxation Strategy (relax brand/powertrain/budget)"]
    Q --> P
    P -->|Tidak| R["VIKOR Ranking: hitung S, R, Q"]
    R --> S["Validate Compromise Solution"]
    S --> T["Generate Car Insights (Explainer)"]
    T --> U["Simpan History ke SQLite"]
    U --> V["Kirim response ke Rasa → Frontend"]
    V --> W["Frontend menampilkan kartu rekomendasi"]
    W --> H
```

### 2.3 Activity Diagram — UC-3: Memilih/Memperbaiki Preferensi

```mermaid
flowchart TD
    A([Start]) --> B["User mengirim pesan preferensi tambahan"]
    B --> C["Rasa NLU: Deteksi intent choose_preference"]
    C --> D["ActionRecommendCar: extract_entities()"]
    D --> E["DialogueContextManager: merge context lama + baru"]
    E --> F{"Butuh refinement? (powertrain/fitur/seat belum ada)"}
    F -->|Ya| G["Chatbot meminta refinement (utter_ask_refinement)"]
    G --> H([End])
    F -->|Tidak| I["Kirim merged payload ke FastAPI /chat"]
    I --> J["PreferenceBuilder membangun parameter gabungan"]
    J --> K["VIKOR Ranking ulang dengan preferensi terbaru"]
    K --> L["Response dikirim ke Frontend"]
    L --> M["Frontend menampilkan rekomendasi yang diperbarui"]
    M --> H
```

### 2.4 Activity Diagram — UC-4: Membandingkan Budget

```mermaid
flowchart TD
    A([Start]) --> B["User meminta perbandingan dengan budget lebih tinggi"]
    B --> C["Rasa NLU: Deteksi intent ask_comparison"]
    C --> D["ActionCompareBudget: ambil budget lama dari slot"]
    D --> E["Parsing budget baru dari pesan"]
    E --> F{"Budget baru valid?"}
    F -->|Tidak| G["Chatbot meminta budget baru"]
    G --> H([End])
    F -->|Ya| I["Kirim payload ke FastAPI /chat dengan previous_max_budget"]
    I --> J["FastAPI: Jalankan VIKOR dengan budget lama (base)"]
    J --> K["FastAPI: Jalankan VIKOR dengan budget baru"]
    K --> L["Explainer: compare_two_cars()"]
    L --> M["Response + comparison_insight dikirim ke Frontend"]
    M --> N["Frontend menampilkan hasil perbandingan"]
    N --> H
```

### 2.5 Activity Diagram — UC-5: Mengatur Bobot Kriteria Manual

```mermaid
flowchart TD
    A([Start]) --> B["User menekan tombol 'Cari Sekarang' di chatbot"]
    B --> C["Rasa mengirim payload ask_weights ke Frontend"]
    C --> D["Frontend menampilkan slider bobot (ManualWeightInput)"]
    D --> E["User mengatur slider (Performa, Irit, Nyaman, dll.)"]
    E --> F["Frontend mengirim manual_weights ke FastAPI /chat"]
    F --> G["FastAPI: Map UI keys → INDEX keys"]
    G --> H["INDEX_PRICE di-force = 10.0"]
    H --> I["VIKOR Ranking dengan bobot manual"]
    I --> J["Response dikirim ke Frontend"]
    J --> K["Frontend menampilkan kartu rekomendasi"]
    K --> L([End])
```

### 2.6 Activity Diagram — UC-6: Melihat Riwayat Pencarian

```mermaid
flowchart TD
    A([Start]) --> B["User membuka halaman riwayat"]
    B --> C["Frontend memanggil GET /history"]
    C --> D["FastAPI: get_recent_history() dari SQLite"]
    D --> E["Data dikembalikan ke Frontend"]
    E --> F["Frontend menampilkan daftar riwayat"]
    F --> G{"User ingin hapus riwayat?"}
    G -->|Tidak| H([End])
    G -->|Ya| I["User klik tombol hapus"]
    I --> J["Frontend memanggil DELETE /history/{id}"]
    J --> K["FastAPI: delete_chat_history() dari SQLite"]
    K --> L["Frontend memperbarui tampilan"]
    L --> H
```

---

## 3. Sequence Diagram

### 3.1 Sequence Diagram — UC-1: Memulai Percakapan

```mermaid
sequenceDiagram
    actor User
    participant FE as Frontend (Next.js)
    participant Rasa as Rasa NLU Server
    
    User->>FE: Mengetik "Halo"
    FE->>Rasa: POST /webhooks/rest/webhook {message: "Halo"}
    Rasa->>Rasa: NLU Pipeline → intent: greet
    Rasa->>FE: response: utter_greet
    FE->>User: Menampilkan "Halo! Saya bisa membantu rekomendasi mobil."
```

### 3.2 Sequence Diagram — UC-2: Meminta Rekomendasi Mobil

```mermaid
sequenceDiagram
    actor User
    participant FE as Frontend (Next.js)
    participant Rasa as Rasa Server
    participant Action as Rasa Action Server
    participant API as FastAPI Backend
    participant PB as PreferenceBuilder
    participant VE as VIKOR Engine
    participant DB as SQLite Database

    User->>FE: "Carikan mobil budget 400jt yang irit"
    FE->>Rasa: POST /webhooks/rest/webhook
    Rasa->>Rasa: NLU: intent=ask_recommendation, entities=[budget:400jt, preference:irit]
    Rasa->>Action: Trigger action_recommend_car
    Action->>Action: extract_entities() → parse budget & preference
    Action->>Action: DialogueContextManager.get_merged_context()
    Action->>API: POST /initial-ui-state {preference_terms, entities}
    API-->>Action: {cluster_name, base_weight_profile}
    Action->>FE: custom: {action: "ask_weights", payload}
    FE->>FE: User mengatur slider bobot
    FE->>API: POST /chat {preferences, weights, budget, entities}
    API->>PB: build_recommendation_params()
    PB->>PB: build_weight_dict() + extract_cluster()
    PB-->>API: params {weight_dict, cluster_name, filters}
    API->>VE: recommend_cars(params)
    VE->>VE: apply_query_guard() → filter_budget() → apply_hard_filters()
    VE->>VE: vikor_rank(df, weight_dict) → S, R, Q
    VE->>VE: validate_compromise_solution()
    VE-->>API: {recommendations, constraint_report}
    API->>API: generate_car_insights() per mobil
    API->>DB: save_chat_history()
    API-->>FE: RecommendationResponse
    FE->>User: Menampilkan kartu rekomendasi mobil
```

### 3.3 Sequence Diagram — UC-3: Memilih/Memperbaiki Preferensi

```mermaid
sequenceDiagram
    actor User
    participant FE as Frontend (Next.js)
    participant Rasa as Rasa Server
    participant Action as Rasa Action Server
    participant API as FastAPI Backend
    participant VE as VIKOR Engine

    User->>FE: "Tambahin fitur sunroof dan 7 seat"
    FE->>Rasa: POST /webhooks/rest/webhook
    Rasa->>Rasa: NLU: intent=choose_preference, entities=[feature:sunroof, min_seat:7]
    Rasa->>Action: Trigger action_recommend_car
    Action->>Action: extract_entities()
    Action->>Action: DialogueContextManager: merge slot lama + entity baru
    Action->>Action: Cek refinement_stage & kelengkapan data
    Action->>FE: custom: {action: "search_cars", payload}
    FE->>API: POST /chat {merged preferences + budget lama + fitur baru}
    API->>API: build_recommendation_params() dengan konteks gabungan
    API->>VE: recommend_cars() dengan filter sunroof & min_seat=7
    VE-->>API: {recommendations, constraint_report}
    API-->>FE: RecommendationResponse
    FE->>User: Menampilkan rekomendasi yang diperbarui
```

### 3.4 Sequence Diagram — UC-4: Membandingkan Budget

```mermaid
sequenceDiagram
    actor User
    participant FE as Frontend (Next.js)
    participant Rasa as Rasa Server
    participant Action as Rasa Action Server
    participant API as FastAPI Backend
    participant VE as VIKOR Engine
    participant EX as Explainer

    User->>FE: "Kalau budgetnya naik 100jt gimana?"
    FE->>Rasa: POST /webhooks/rest/webhook
    Rasa->>Rasa: NLU: intent=ask_comparison
    Rasa->>Action: Trigger action_compare_budget
    Action->>Action: Ambil previous_max_budget dari slot
    Action->>Action: Parsing budget increment dari teks
    Action->>API: POST /chat {previous_max_budget, max_budget baru}
    API->>VE: recommend_cars(budget lama) → base result
    API->>VE: recommend_cars(budget baru) → new result
    API->>EX: compare_two_cars(new_top, base_top, weights)
    EX-->>API: comparison_insight string
    API-->>Action: {recommendations, comparison_insight}
    Action->>FE: Menampilkan pesan perbandingan + insight
    FE->>User: Menampilkan hasil perbandingan budget
```

### 3.5 Sequence Diagram — UC-5: Mengatur Bobot Kriteria Manual

```mermaid
sequenceDiagram
    actor User
    participant FE as Frontend (Next.js)
    participant API as FastAPI Backend
    participant PB as PreferenceBuilder
    participant VE as VIKOR Engine

    User->>FE: Menggeser slider bobot (Performa=8, Irit=6, dst.)
    User->>FE: Klik "Cari Sekarang"
    FE->>API: POST /chat {manual_weights: {performance:8, efficiency:6, ...}}
    API->>API: Map UI keys → INDEX keys via UI_TO_INDEX_MAP
    API->>API: Force INDEX_PRICE = 10.0
    API->>PB: build_recommendation_params()
    PB-->>API: params dengan weight_dict manual
    API->>VE: recommend_cars(weight_dict=manual)
    VE->>VE: build_weight_vector() → normalisasi bobot
    VE->>VE: vikor_rank() → perankingan
    VE-->>API: {recommendations}
    API-->>FE: RecommendationResponse
    FE->>User: Menampilkan kartu rekomendasi sesuai bobot manual
```

### 3.6 Sequence Diagram — UC-6: Melihat Riwayat Pencarian

```mermaid
sequenceDiagram
    actor User
    participant FE as Frontend (Next.js)
    participant API as FastAPI Backend
    participant DB as SQLite Database

    User->>FE: Membuka halaman riwayat
    FE->>API: GET /history
    API->>DB: get_recent_history(limit=20)
    DB-->>API: rows data history
    API->>API: Deserialize JSON fields (preferences, recommendations)
    API-->>FE: List[HistoryItemResponse]
    FE->>User: Menampilkan daftar riwayat pencarian

    opt Hapus Riwayat
        User->>FE: Klik tombol hapus pada record
        FE->>API: DELETE /history/{id}
        API->>DB: delete_chat_history(id)
        DB-->>API: OK
        API-->>FE: {status: "success"}
        FE->>User: Riwayat dihapus, tampilan diperbarui
    end
```

---

## 4. Class Diagram

```mermaid
classDiagram
    direction TB

    class RasaNLU {
        +WhitespaceTokenizer
        +RegexFeaturizer
        +CountVectorsFeaturizer
        +DIETClassifier
        +EntitySynonymMapper
        +classify_intent(text) Intent
        +extract_entities(text) List~Entity~
    }

    class ActionRecommendCar {
        +name() String
        +run(dispatcher, tracker, domain) List~SlotSet~
        -extract_entities(entities, text) Dict
        -format_car_recommendation(cars) String
    }

    class ActionCompareBudget {
        +name() String
        +run(dispatcher, tracker, domain) List~SlotSet~
    }

    class DialogueContextManager {
        -tracker: Tracker
        -new_parsed: Dict
        -reset_context: bool
        -negated: List~str~
        -_get_prev(slot_name) List
        -_unique_clean(lst) List
        -_merge_and_strip(current, prev) List
        +get_merged_context() Dict
    }

    class FastAPIApp {
        +root() Dict
        +recommend(request) RecommendationResponse
        +chat(request) RecommendationResponse
        +get_initial_ui_state(request) Dict
        +get_chat_history() List~HistoryItemResponse~
        +delete_history(id) Dict
        +feature_summary() Dict
    }

    class ChatRequest {
        +user_message: str
        +preference_terms: List~str~
        +need_terms: List~str~
        +weight_input: Dict
        +entities: List~str~
        +negated_terms: List~str~
        +raw_budgets: List~str~
        +min_budget: int
        +max_budget: int
        +manual_weights: Dict
        +top_n: int
    }

    class RecommendationResponse {
        +recommendations: List~CarRecommendation~
        +constraint_report: Dict
        +comparison_insight: str
    }

    class CarRecommendation {
        +BRAND: str
        +MODEL: str
        +VARIAN: str
        +HARGAOTR: int
        +CLUSTER_NAME: str
        +VIKOR_Q: float
        +VIKOR_S: float
        +VIKOR_R: float
        +VIKOR_STATUS: str
        +insight: str
    }

    class HistoryItemResponse {
        +id: int
        +user_message: str
        +timestamp: str
        +nlp_preferences: List~str~
        +cluster_name: str
        +cars_total: int
        +top_recommendations: List~CarRecommendation~
    }

    class PreferenceBuilder {
        +build_weight_dict(prefs, weights) Dict
        +extract_body_type(entities) str
        +extract_powertrain(entities) str
        +extract_drive_sys(entities) str
        +extract_cluster(terms) List~str~
        +extract_brand(entities) str
        +build_feature_constraints(entities) Dict
        +build_hard_filters(entities) Dict
        +build_recommendation_params(prefs, weights, entities) Dict
    }

    class FeatureOntology {
        +PREFERENCE_INDEX_MAP: Dict
        +PREFERENCE_CLUSTER_MAP: Dict
        +NEED_CLUSTER_MAP: Dict
        +BODY_TYPE_MAP: Dict
        +POWERTRAIN_MAP: Dict
        +BRAND_MAP: Dict
        +UI_TO_INDEX_MAP: Dict
        +CLUSTER_PROFILES: Dict
    }

    class AgglomerativeClustering {
        +CLUSTER_FEATURES: List~str~
        +build_feature_matrix(df) Tuple
        +detect_optimal_clusters(X) int
        +assign_cluster_profiles(df) Tuple
        +perform_clustering(df) DataFrame
        +generate_dendrogram(X, path) void
    }

    class VIKORAlgorithm {
        +VIKOR_CRITERIA: List~str~
        +build_weight_vector(weight_dict, criteria) ndarray
        +vikor_rank(df, weight_dict, v) DataFrame
        +validate_compromise_solution(df) DataFrame
    }

    class RankingEngine {
        +DF_CARS: DataFrame
        +FEATURE_SUMMARY: Dict
        +init_dataset() DataFrame
        +filter_budget(df, max, min) DataFrame
        +filter_brand(df, brand) DataFrame
        +apply_hard_filters(df, kwargs) DataFrame
        +recommend_cars(weight_dict, cluster, budget, ...) Dict
    }

    class Explainer {
        +INDEX_LABELS: Dict
        +generate_car_insights(car, weights) str
        +compare_two_cars(car_a, car_b, weights) str
    }

    class Database {
        +DB_PATH: str
        +init_db() void
        +save_chat_history(...) void
        +get_recent_history(limit) List~Dict~
        +delete_chat_history(id) void
    }

    class QueryGuard {
        +apply_query_guard(df, body_type, powertrain, ...) Tuple
        +parse_budget_strings(raw_budgets) Tuple
    }

    class FrontendApp {
        +ChatPage: Component
        +Navbar: Component
        +CarCard: Component
        +ManualWeightInput: Component
        +ElasticSlider: Component
    }

    %% Relationships
    FrontendApp --> RasaNLU : sends message
    RasaNLU --> ActionRecommendCar : triggers
    RasaNLU --> ActionCompareBudget : triggers
    ActionRecommendCar --> DialogueContextManager : uses
    ActionRecommendCar --> FastAPIApp : HTTP POST /chat
    ActionCompareBudget --> FastAPIApp : HTTP POST /chat
    FastAPIApp --> ChatRequest : receives
    FastAPIApp --> RecommendationResponse : returns
    FastAPIApp --> PreferenceBuilder : delegates
    FastAPIApp --> RankingEngine : calls recommend_cars()
    FastAPIApp --> Explainer : generates insights
    FastAPIApp --> Database : persists history
    PreferenceBuilder --> FeatureOntology : reads mappings
    RankingEngine --> AgglomerativeClustering : init clustering
    RankingEngine --> VIKORAlgorithm : ranking
    RankingEngine --> QueryGuard : filtering
    RecommendationResponse *-- CarRecommendation
    HistoryItemResponse *-- CarRecommendation
    FrontendApp --> FastAPIApp : HTTP GET/DELETE /history
```
