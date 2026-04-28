# UML Diagrams - Car Recommendation Chatbot

Berikut adalah representasi diagram Use Case, Activity, Sequence, dan Class untuk proyek Chatbot Rekomendasi Mobil Anda. Diagram-diagram ini dibuat menggunakan Mermaid JS berdasarkan struktur *codebase* Anda.

## 1. Use Case Diagram
Diagram ini menunjukkan fungsionalitas sistem yang dapat diakses oleh *User* dan *Admin/Tester*.

```mermaid
flowchart LR
    User([User])
    Admin([Admin / Tester])

    subgraph System [Car Recommendation Chatbot]
        UC1(Mulai Percakapan / Input Preferensi)
        UC2(Dapatkan Rekomendasi Mobil)
        UC3(Atur Bobot Manual Slider UI)
        UC4(Lihat Insight / Penjelasan Mobil)
        UC5(Lihat Riwayat Percakapan)
        UC6(Lihat Hasil Evaluasi Model)
    end

    User --> UC1
    User --> UC2
    User --> UC3
    User --> UC4
    User --> UC5
    Admin --> UC6
    UC1 -.->|include| UC2
```

## 2. Activity Diagram
Diagram ini menggambarkan alur aktivitas dari sistem, mulai dari pengguna memberikan input chat hingga mendapatkan output rekomendasi akhir beserta *insight*-nya.

```mermaid
stateDiagram-v2
    [*] --> InputChat
    InputChat : User memasukkan chat (Preferensi/Kebutuhan)
    InputChat --> NLUExtract
    NLUExtract : Frontend kirim pesan ke Rasa NLU
    NLUExtract --> MapFeatures
    MapFeatures : Rasa mengekstrak intent & entities (budget, need, dll)
    MapFeatures --> SendToBackend
    SendToBackend : Frontend kirim state NLU & Manual Weights ke Backend (/chat)
    SendToBackend --> ParseConstraints
    ParseConstraints : Backend memparsing batasan budget, kapasitas kursi, dll.
    ParseConstraints --> DetermineCluster
    DetermineCluster : Backend menentukan cluster mobil (Family, dll)
    DetermineCluster --> VikorRanking
    VikorRanking : Backend menjalankan VIKOR Ranking Engine (recommend_cars)
    VikorRanking --> GenerateInsights
    GenerateInsights : Backend men-generate insight & teks penjelasan komparasi
    GenerateInsights --> SaveHistory
    SaveHistory : Backend menyimpan riwayat chat ke Database SQLite
    SaveHistory --> ShowRecommendation
    ShowRecommendation : Frontend menerima respons dan menampilkan daftar mobil
    ShowRecommendation --> [*]
```

## 3. Sequence Diagram
Diagram sekuensi ini menunjukkan urutan interaksi antar komponen (*Frontend*, *Rasa*, *FastAPI Backend*, dan *VIKOR Engine*) secara kronologis saat *user* meminta rekomendasi.

```mermaid
sequenceDiagram
    actor User
    participant Frontend as Next.js Frontend
    participant Rasa as Rasa NLP
    participant Backend as FastAPI Backend
    participant Vikor as VIKOR Engine
    participant Database as SQLite DB

    User->>Frontend: Kirim pesan "Cari mobil irit untuk keluarga"
    activate Frontend
    Frontend->>Rasa: POST /model/parse (Kirim Teks Chat)
    activate Rasa
    Rasa-->>Frontend: Response (Intent: ask_recommendation, Entities: [irit, keluarga])
    deactivate Rasa
    
    Frontend->>Backend: POST /chat (Kirim Entities + UI Manual Weights)
    activate Backend
    Backend->>Backend: build_recommendation_params()
    Backend->>Backend: Parsing Constraints & Tentukan Cluster
    
    Backend->>Vikor: recommend_cars(params, top_n)
    activate Vikor
    Vikor-->>Backend: Kembalikan List Mobil Terbaik & Laporan Constraint
    deactivate Vikor
    
    Backend->>Backend: generate_car_insights(Top Cars)
    
    Backend->>Database: save_chat_history()
    activate Database
    Database-->>Backend: Success
    deactivate Database
    
    Backend-->>Frontend: RecommendationResponse (List Mobil + Insight)
    deactivate Backend
    
    Frontend-->>User: Tampilkan Kartu Rekomendasi Mobil
    deactivate Frontend
```

## 4. Class Diagram
Diagram ini memvisualisasikan struktur fungsi utama, dependensi modul internal, dan skema pydantic yang digunakan di dalam `FastAPI Backend`.

```mermaid
classDiagram
    class FastAPI_Main {
        +recommend(request: RecommendationRequest)
        +get_initial_ui_state(request: ChatRequest)
        +chat(request: ChatRequest)
        +get_chat_history()
        +eval_clustering()
        +eval_rekomendasi()
    }

    class ChatRequest {
        +String user_message
        +List preference_terms
        +List need_terms
        +Dict weight_input
        +List entities
        +Int min_budget
        +Int max_budget
        +Dict manual_weights
    }

    class RecommendationResponse {
        +List~CarRecommendation~ recommendations
        +Dict constraint_report
        +String comparison_insight
    }

    class CarRecommendation {
        +String BRAND
        +String MODEL
        +String VARIAN
        +Float VIKOR_Q
        +Float INDEX_PRICE
        +String BODY_TYPE
        +Float CC
        +String insight
    }

    class VikorEngine {
        +recommend_cars(weight_dict, brand, cluster_name, top_n, constraints)
        +get_feature_summary()
    }

    class DatabaseManager {
        +init_db()
        +save_chat_history(...)
        +get_recent_history()
        +delete_chat_history(id)
    }

    class Explainer {
        +generate_car_insights(car, weights)
        +compare_two_cars(new_car, base_car, weights)
    }

    class QueryGuard {
        +parse_budget_strings(raw_budgets)
    }

    class PreferenceBuilder {
        +build_recommendation_params(preference_terms, weight_input, entities)
    }

    FastAPI_Main ..> ChatRequest : Menerima
    FastAPI_Main ..> RecommendationResponse : Mengembalikan
    RecommendationResponse o-- CarRecommendation : Berisi
    FastAPI_Main --> VikorEngine : Memanggil
    FastAPI_Main --> DatabaseManager : Menggunakan
    FastAPI_Main --> Explainer : Menggunakan
    FastAPI_Main --> QueryGuard : Menggunakan
    FastAPI_Main --> PreferenceBuilder : Menggunakan
```
