# Use Case & Activity Diagram — Chatbot Rekomendasi Mobil (Otobot)

---

## 1. Use Case Diagram

```mermaid
graph LR
    subgraph Otobot["Sistem Otobot"]
        UC1["Input Kebutuhan Mobil"]
        UC2["Mengatur Bobot Kriteria (Slider)"]
        UC3["Melihat Top 5 Rekomendasi"]
        SYS1["Proses Intent & Filtering"]
        SYS2["Penentuan Cluster"]
        SYS3["Perhitungan VIKOR"]
    end

    User(("👤 User"))

    User --> UC1
    User --> UC2
    User --> UC3

    UC1 -.->|"≪include≫"| SYS1
    UC1 -.->|"≪include≫"| SYS2
    UC2 -.->|"≪extend≫"| UC1
    UC3 -.->|"≪include≫"| SYS3
    SYS1 -.->|"≪include≫"| SYS3
```

### Tabel Deskripsi Use Case

| UC | Nama | Aktor | Deskripsi | Relasi |
|----|------|-------|-----------|--------|
| UC-1 | Input Kebutuhan Mobil | User | User mengirim pesan berisi budget, preferensi, dan kebutuhan mobil melalui chatbot | `<<include>>` Proses Intent & Filtering, `<<include>>` Penentuan Cluster |
| UC-2 | Mengatur Bobot Kriteria (Slider) | User | User mengatur slider bobot prioritas (Performa, Irit, Nyaman, dll.) sebelum pencarian dijalankan | `<<extend>>` Input Kebutuhan Mobil (opsional) |
| UC-3 | Melihat Top 5 Rekomendasi | User | User melihat hasil 5 rekomendasi mobil terbaik beserta insight dan skor VIKOR | `<<include>>` Perhitungan VIKOR |

### Tabel Deskripsi Proses Sistem

| Proses | Deskripsi | Di-include oleh |
|--------|-----------|-----------------|
| Proses Intent & Filtering | Rasa NLU mengklasifikasikan intent dan mengekstraksi entity (budget, preference, brand, dll.), lalu QueryGuard memfilter dataset | UC-1, dan include ke Perhitungan VIKOR |
| Penentuan Cluster | Sistem mencocokkan preferensi user ke cluster HAC yang sudah terbentuk saat startup (Urban Agility, Family Comfort, dll.) | UC-1 |
| Perhitungan VIKOR | Algoritma VIKOR menghitung skor S, R, Q dan meranking mobil berdasarkan bobot kriteria | UC-3, di-include dari Proses Intent & Filtering |

### Penjelasan Relasi

- **`<<include>>`**: Proses yang **wajib** dijalankan. Contoh: UC-1 selalu memicu Proses Intent & Filtering.
- **`<<extend>>`**: Proses **opsional**. UC-2 (slider) memperluas UC-1 — user bisa langsung dapat rekomendasi tanpa mengatur slider (sistem menggunakan bobot default dari NLP).

---

## 2. Activity Diagram

### 2.1 Activity Diagram — UC-1: Input Kebutuhan Mobil

```mermaid
flowchart TD
    A([Mulai]) --> B["User mengirim pesan ke chatbot\n(contoh: 'carikan mobil budget 400jt yang irit')"]
    B --> C["Rasa NLU: Klasifikasi Intent"]
    C --> D{"Intent terdeteksi?"}
    D -->|"greet"| E["Chatbot membalas sapaan\n(utter_greet)"]
    E --> F([Selesai])
    D -->|"out_of_scope / nlu_fallback"| G["Chatbot membalas fallback\n(utter_default)"]
    G --> F
    D -->|"ask_recommendation / choose_preference / start_search"| H["Rasa NLU: Ekstraksi Entity\n(budget, preference, brand, body_type,\npowertrain, feature, hard_filter, need)"]
    H --> I["ActionRecommendCar: extract_entities()"]
    I --> J["DialogueContextManager:\nMerge konteks lama + baru,\nHapus negated entities"]
    J --> K{"Ada budget di konteks?"}
    K -->|Tidak| L["Chatbot meminta budget\n(utter_ask_budget)"]
    L --> F
    K -->|Ya| M{"Ada preferensi di konteks?"}
    M -->|Tidak| N["Chatbot meminta preferensi\n(utter_ask_initial_preference)"]
    N --> F
    M -->|Ya| O{"Butuh refinement?\n(powertrain/fitur/seat belum ada\ndan refinement_stage = false)"}
    O -->|Ya| P["Chatbot meminta detail tambahan\n(utter_ask_refinement)"]
    P --> F
    O -->|Tidak| Q["Kirim payload ke FastAPI /chat"]
    Q --> R["PreferenceBuilder:\nbuild_recommendation_params()"]
    R --> S["Proses berlanjut ke\nPenentuan Cluster & Perhitungan VIKOR"]
    S --> F
```

### 2.2 Activity Diagram — UC-2: Mengatur Bobot Kriteria (Slider)

```mermaid
flowchart TD
    A([Mulai]) --> B["Rasa mengirim payload ask_weights\nke Frontend beserta base_weight_profile"]
    B --> C["Frontend menampilkan\nkomponen ManualWeightInput\n(slider untuk setiap kriteria)"]
    C --> D["User menggeser slider bobot:\nPerforma, Irit BBM, Kenyamanan,\nTeknologi, Keamanan, dll."]
    D --> E["User menekan tombol\n'Cari Sekarang'"]
    E --> F["Frontend mengirim manual_weights\nlangsung ke FastAPI POST /chat\n(TANPA melalui Rasa NLU)"]
    F --> G["FastAPI: Map UI keys → INDEX keys\nvia UI_TO_INDEX_MAP"]
    G --> H["Force INDEX_PRICE = 10.0\n(Value for Money selalu prioritas)"]
    H --> I["Proses berlanjut ke\nPerhitungan VIKOR dengan bobot manual"]
    I --> J([Selesai])
```

### 2.3 Activity Diagram — UC-3: Melihat Top 5 Rekomendasi

```mermaid
flowchart TD
    A([Mulai]) --> B["Menerima parameter dari\nUC-1 (Input Kebutuhan) dan/atau\nUC-2 (Bobot Manual)"]
    B --> C["Penentuan Cluster:\nCocokkan preferensi user ke\nlabel cluster HAC yang sudah ada\n(Urban Agility, Family Comfort, dll.)"]
    C --> D["Apply Query Guard:\nFilter berdasarkan body_type,\npowertrain, drive_sys, negated_terms"]
    D --> E["Apply Hard Filters:\nmin_seat, min_ground_clearance,\nmust_have_sunroof, must_have_wireless_tech"]
    E --> F["Apply Budget Filter:\nmin_budget ≤ HARGAOTR ≤ max_budget"]
    F --> G{"Dataset kosong\nsetelah filtering?"}
    G -->|Ya| H["Relaxation Strategy:\n1. Abaikan Brand\n2. Abaikan Powertrain\n3. Naikkan budget 1.3x"]
    H --> G
    G -->|Tidak| I["Soft Constraint:\nBoost INDEX_CLUSTER_MATCH\nuntuk mobil yang cocok cluster"]
    I --> J["VIKOR Ranking:\nHitung Decision Matrix,\nS (Group Utility),\nR (Individual Regret),\nQ = v·S* + (1-v)·R*"]
    J --> K["Validate Compromise Solution:\nCek Condition 1 (DQ threshold)\nCek Condition 2 (S/R terbaik)"]
    K --> L["Ambil Top 5 hasil ranking"]
    L --> M["Generate Car Insights\nper mobil via Explainer"]
    M --> N["Simpan riwayat pencarian\nke SQLite Database"]
    N --> O["Kirim RecommendationResponse\nke Frontend"]
    O --> P["Frontend menampilkan\n5 kartu rekomendasi mobil\ndengan insight & skor VIKOR"]
    P --> Q([Selesai])
```

---

## 3. Mapping Use Case ↔ Activity

| Use Case | Activity Diagram | Proses Sistem yang Terlibat |
|----------|-----------------|----------------------------|
| UC-1: Input Kebutuhan Mobil | AD 2.1 | Proses Intent & Filtering, Penentuan Cluster |
| UC-2: Mengatur Bobot Kriteria | AD 2.2 | — (langsung ke VIKOR, bypass NLU) |
| UC-3: Melihat Top 5 Rekomendasi | AD 2.3 | Penentuan Cluster, Perhitungan VIKOR |

> [!NOTE]
> Alur normal lengkap: **UC-1** → *(opsional)* **UC-2** → **UC-3**
> - User input kebutuhan (UC-1)
> - Sistem minta bobot slider, user atur (UC-2, extend/opsional)
> - Sistem proses VIKOR dan tampilkan hasil (UC-3)
