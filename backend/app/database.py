import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Any
from app.feature_ontology import DRIVETRAIN_DECODING


DB_PATH = os.path.join(os.path.dirname(__file__), "history.db")

def init_db():
    """Inisialisasi tabel chat_history di SQLite."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            
            nlp_preferences TEXT,
            nlp_needs TEXT,
            nlp_entities TEXT,
            
            cluster_name TEXT,
            hard_filters_applied TEXT,
            weight_dict_used TEXT,
            
            cars_total INTEGER,
            cars_after_constraint INTEGER,
            top_recommendations TEXT
        )
    """)
    # Auto-migrate: add weight_dict_used column if missing
    try:
        cursor.execute("SELECT weight_dict_used FROM chat_history LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE chat_history ADD COLUMN weight_dict_used TEXT DEFAULT '{}'")
    conn.commit()
    conn.close()

def save_chat_history(
    user_message: str,
    nlp_preferences: List[str],
    nlp_needs: List[str],
    nlp_entities: List[str],
    cluster_name: str,
    hard_filters_applied: Dict[str, Any],
    cars_total: int,
    cars_after_constraint: int,
    top_recommendations: List[Dict[str, Any]],
    weight_dict_used: Dict[str, float] = None
):
    """Menyimpan satu record evaluasi pencarian ke database."""
    nlp_preferences_json = json.dumps(nlp_preferences)
    nlp_needs_json = json.dumps(nlp_needs)
    nlp_entities_json = json.dumps(nlp_entities)
    hard_filters_json = json.dumps(hard_filters_applied)
    recommendations_json = json.dumps(top_recommendations)
    weight_dict_json = json.dumps(weight_dict_used or {})

    timestamp = datetime.now().isoformat()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO chat_history (
            user_message, timestamp,
            nlp_preferences, nlp_needs, nlp_entities,
            cluster_name, hard_filters_applied, weight_dict_used,
            cars_total, cars_after_constraint, top_recommendations
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_message, timestamp,
        nlp_preferences_json, nlp_needs_json, nlp_entities_json,
        cluster_name, hard_filters_json, weight_dict_json,
        cars_total, cars_after_constraint, recommendations_json
    ))
    conn.commit()
    conn.close()

def get_recent_history(limit: int = 15) -> List[Dict[str, Any]]:
    """Mengambil history terbaru dari database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM chat_history ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()

    result = []
    for row in rows:
        item = dict(row)
        item["nlp_preferences"] = json.loads(item["nlp_preferences"]) if item["nlp_preferences"] else []
        item["nlp_needs"] = json.loads(item["nlp_needs"]) if item["nlp_needs"] else []
        item["nlp_entities"] = json.loads(item["nlp_entities"]) if item["nlp_entities"] else []
        item["hard_filters_applied"] = json.loads(item["hard_filters_applied"]) if item["hard_filters_applied"] else {}
        item["top_recommendations"] = json.loads(item["top_recommendations"]) if item["top_recommendations"] else []
        item["weight_dict_used"] = json.loads(item.get("weight_dict_used") or "{}") if item.get("weight_dict_used") else {}
        
        # Sanitize recommendations to ensure DRIVE_SYS and POWERTRAIN are strings (fixes Pydantic validation errors)
        for car in item["top_recommendations"]:
            if "DRIVE_SYS" in car and car["DRIVE_SYS"] is not None:
                val = car["DRIVE_SYS"]
                try:
                    # Jika numeric label (float/int), decode menggunakan ontologi
                    car["DRIVE_SYS"] = DRIVETRAIN_DECODING.get(float(val), str(val))
                except (ValueError, TypeError):
                    car["DRIVE_SYS"] = str(val)
            
            if "POWERTRAIN" in car and car["POWERTRAIN"] is not None:
                car["POWERTRAIN"] = str(car["POWERTRAIN"])

        result.append(item)
    
    return result

def delete_chat_history(history_id: int):
    """Menghapus satu record history berdasarkan ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_history WHERE id=?", (history_id,))
    conn.commit()
    conn.close()
