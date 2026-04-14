
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

class SemanticMapper:
    """
    Scientific way to map user natural language preferences to 
    system criteria using Vector Space Model (TF-IDF + Cosine Similarity).
    """
    def __init__(self, target_keywords: List[str]):
        self.target_keywords = target_keywords
        self.vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5))
        if target_keywords:
            self.target_vectors = self.vectorizer.fit_transform(target_keywords)
        else:
            self.target_vectors = None

    def find_best_match(self, query: str, threshold: float = 0.3) -> List[Tuple[str, float]]:
        """
        Finds the most semantically similar keywords from the target list.
        """
        if self.target_vectors is None or not query:
            return []

        query_vec = self.vectorizer.transform([query.lower()])
        similarities = cosine_similarity(query_vec, self.target_vectors).flatten()
        
        results = []
        for i, score in enumerate(similarities):
            if score >= threshold:
                results.append((self.target_keywords[i], float(score)))
        
        # Sort by score descending
        results.sort(key=lambda x: x[1], reverse=True)
        return results

# Global instances cache
_mappers = {}

def get_mapper(name: str, target_keywords: List[str]) -> SemanticMapper:
    if name not in _mappers:
        _mappers[name] = SemanticMapper(target_keywords)
    return _mappers[name]
