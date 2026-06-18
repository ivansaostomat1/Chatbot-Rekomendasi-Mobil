import os
import sys
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import euclidean_distances, cosine_similarity

# Path injection for app package
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from app.data_loader import load_all_datasets
from app.feature_engineering.pipeline import generate_feature_dataset

try:
    # pyrefly: ignore [missing-import]
    from unidecode import unidecode
except ImportError:
    def unidecode(text):
        import unicodedata
        return unicodedata.normalize('NFKD', str(text)).encode('ascii', 'ignore').decode('utf-8')

def normalize_text(text):
    if not text: return ""
    return unidecode(str(text)).lower().strip()

class KMeansEngine:
    def __init__(self, n_clusters=8, random_state=42):
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.kmeans = KMeans(n_clusters=self.n_clusters, random_state=self.random_state, n_init=10)
        self.scaler = StandardScaler()
        self.df = None
        self.features_normalized = None
        self.features_list = [
            # 'HARGAOTR', 
            'HORSE POWER (HP)', 
            'TORQUE (Nm)', 
            'GROUND CLEARANCE', 
            'WHEELBASE', 
            'LONG', 
            'WIDTH', 
            'HEIGHT'
        ]
        self._initialize()

    def _initialize(self):
        mobil, wholesales, retail = load_all_datasets()
        self.df = generate_feature_dataset(mobil, wholesales, retail)
        
        # Fill missing values with median
        for feature in self.features_list:
            if feature in self.df.columns:
                self.df[feature] = self.df[feature].fillna(self.df[feature].median())
        
        # Extract features for clustering
        X = self.df[self.features_list].values
        self.features_normalized = self.scaler.fit_transform(X)
        
        # Train KMeans
        self.df['CLUSTER'] = self.kmeans.fit_predict(self.features_normalized)
        
        # Create a searchable full name column for disambiguation
        self.df['SEARCH_NAME'] = (self.df['BRAND'] + " " + self.df['MODEL'] + " " + self.df['VARIAN']).apply(lambda x: normalize_text(x))

    def search_car_models(self, query: str):
        """
        Mencari mobil berdasarkan query string, berguna untuk disambiguasi.
        Returns list of dicts.
        """
        if not query:
            return []
        
        query_norm = normalize_text(query.strip())
        
        # Normalisasi sinonim brand agar cocok dengan database
        import re
        synonyms = {
            r"\bmercedes[- ]benz\b": "mercedes-benz",
            r"\bmerc(?:y|i|s)?\b": "mercedes-benz",
            r"\bmercedes\b": "mercedes-benz",
            r"\bvw\b": "volkswagen",
            r"\bnisan\b": "nissan",
            r"\bmitsu\b": "mitsubishi",
            r"\bcherry\b": "chery",
            r"\bcitroen\b": "citroën"
        }
        for pattern, replacement in synonyms.items():
            query_norm = re.sub(pattern, replacement, query_norm)

        filler_words = {
            "mobil", "yang", "cari", "tampilkan", "rekomendasi", "alternatif", 
            "mirip", "dengan", "sama", "dong", "sih", "deh", "lah", "kah", 
            "ya", "kok", "aja", "saja", "pun", "irit", "hemat", "bbm", 
            "sporty", "sport", "performa", "kencang", "ngebut", "responsif", 
            "tenaga", "nanjak", "lincah", "gesit", "handling", "enak", 
            "dikendarai", "fun", "stabil", "nyaman", "keluarga", "luas", 
            "kabinnya", "kabin", "aman", "teknologi", "fitur", "lengkap", 
            "modern", "canggih", "mewah", "luxury", "banjir", "bebas", 
            "rusak", "jalan", "merek", "brand", "terkenal", "laku", "populer", 
            "baru", "sparepart", "harga", "murah", "bagus"
        }
        query_parts = [p for p in query_norm.split() if p not in filler_words and len(p) > 1]
        
        if not query_parts:
            # Fallback jika query hanya berisi kata pengisi
            query_parts = query_norm.split()

        # Cari yang mengandung semua kata kunci (setelah difilter)
        mask = self.df['SEARCH_NAME'].apply(lambda x: all(part in x for part in query_parts))
        matches = self.df[mask]
        
        # Group by BRAND and MODEL to avoid showing every single variant
        grouped = matches.groupby(['BRAND', 'MODEL'])
        
        results = []
        for (brand, model), group in grouped:
            first_row = group.iloc[0]
            varian_count = len(group)
            
            # Jika semua harga NaN, berikan 0
            try:
                raw_min = group['HARGAOTR'].min()
                raw_max = group['HARGAOTR'].max()
                harga_min = int(raw_min) if not pd.isna(raw_min) else 0
                harga_max = int(raw_max) if not pd.isna(raw_max) else 0
            except:
                harga_min = 0
                harga_max = 0
            
            results.append({
                "brand": brand,
                "model": model,
                "varian": "", # Mengosongkan varian agar pencarian fallback ke seluruh model
                "varian_count": varian_count,
                "harga_min": harga_min,
                "harga_max": harga_max,
                "body_type": first_row.get('BODY TYPE', first_row.get('BODY_TYPE', 'Unknown'))
            })
            
        # Urutkan berdasarkan kemiripan panjang string (semakin pendek semakin relevan)
        results = sorted(results, key=lambda x: len(x['brand'] + ' ' + x['model']))
        
        # 4. Filter Relevansi Tambahan: Jika ada hasil yang EXACT match dengan Brand+Model, ambil itu saja
        clean_query = " ".join(query_parts)
        exact_model_matches = [r for r in results if normalize_text(r['brand'] + " " + r['model']) == clean_query]
        if len(exact_model_matches) == 1:
            print(f"[K-MEANS] Exact model match found: {exact_model_matches[0]['brand']} {exact_model_matches[0]['model']}")
            return exact_model_matches

        return results

    def find_similar_cars(self, brand: str, model: str, varian: str = None, top_n: int = 5):
        """
        Mencari mobil mirip (nearest neighbors) di cluster yang sama menggunakan Euclidean distance.
        Jika varian tidak dispesifikasikan (atau string kosong), akan merata-rata fitur dari seluruh varian model tersebut.
        """
        if varian and str(varian).strip():
            target = self.df[
                (self.df['BRAND'] == brand) & 
                (self.df['MODEL'] == model) & 
                (self.df['VARIAN'] == varian)
            ]
        else:
            target = self.df[
                (self.df['BRAND'] == brand) & 
                (self.df['MODEL'] == model)
            ]
        
        print(f"[K-MEANS] Finding similar for Brand: {brand}, Model: {model}, Varian: {varian}")
        
        if target.empty:
            print(f"[K-MEANS] [ERROR] Target empty for {brand} {model} {varian}")
            return {"error": "Target car not found", "recommendations": []}
            
        if len(target) > 1:
            # Rata-ratakan fitur (DNA) dari semua varian di model ini
            target_indices = target.index
            target_features = np.mean(self.features_normalized[target_indices], axis=0).reshape(1, -1)
            target_cluster = target['CLUSTER'].mode()[0]
        else:
            target_idx = target.index[0]
            target_cluster = self.df.loc[target_idx, 'CLUSTER']
            target_features = self.features_normalized[target_idx].reshape(1, -1)
        
        # Ambil semua mobil di cluster yang sama, kecuali target itu sendiri (semua variannya)
        cluster_mask = (self.df['CLUSTER'] == target_cluster) & (~self.df.index.isin(target.index))
        cluster_df = self.df[cluster_mask]
        
        if cluster_df.empty:
            return {"error": "No similar cars found in the same cluster", "recommendations": []}
            
        cluster_indices = cluster_df.index
        cluster_features = self.features_normalized[cluster_indices]
        
        # Hitung Cosine Similarity (Permintaan User)
        similarities = cosine_similarity(target_features, cluster_features)[0]
        
        # Tambahkan skor ke dataframe
        cluster_df = cluster_df.copy()
        cluster_df['SIMILARITY_SCORE'] = similarities
        
        # Sort dari yang paling mirip (Descending)
        cluster_df = cluster_df.sort_values(by='SIMILARITY_SCORE', ascending=False)
        
        # Group by BRAND and MODEL to ensure we don't return 5 variants of the same car
        unique_recommendations = cluster_df.groupby(['BRAND', 'MODEL']).first().reset_index()
        unique_recommendations = unique_recommendations.sort_values(by='SIMILARITY_SCORE', ascending=False)
        
        top_matches = unique_recommendations.head(top_n).copy()
        
        # Map SIMILARITY_SCORE ke VIKOR_Q (0.0 = 100%, 1.0 = 0%)
        # Karena Cosine: 1.0 = Identik, maka VIKOR_Q = 1 - Cosine
        top_matches['VIKOR_Q'] = 1 - top_matches['SIMILARITY_SCORE']
        
        # Format return seperti VIKOR return (menggunakan uppercase dict)
        records = top_matches.to_dict(orient='records')
        
        # Formatting & Decoding using shared logic
        from app.feature_ontology import TRANSMISSION_DECODING, DRIVETRAIN_DECODING
        from app.data_formatter import format_car_records
        
        # Ensure all columns exist before renaming (pop)
        for r in records:
            r['BODY_TYPE'] = r.pop('BODY TYPE', None)
            r['HORSE_POWER'] = r.pop('HORSE POWER (HP)', None)
            r['TORQUE'] = r.pop('TORQUE (Nm)', None)
            r['GROUND_CLEARANCE'] = r.pop('GROUND CLEARANCE', None)
            r['BATTERY'] = r.pop('BATTERY (KWH)', None)
            r['VIKOR_STATUS'] = "Look-alike (K-Means)"
            
        records = format_car_records(records, TRANSMISSION_DECODING, DRIVETRAIN_DECODING)
        
        return {
            "target": {
                "brand": brand,
                "model": model,
                "varian": varian
            },
            "recommendations": records
        }

# Singleton instance
clustering_engine = KMeansEngine()
