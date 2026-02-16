"""
TF-IDF Embedding Service
Provides text embedding using TF-IDF vectorization
"""

import time
import logging
import re
import pickle
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


class TFidfEmbeddingService:
    """
    TF-IDF based embedding service for text similarity
    """
    
    def __init__(self, max_features: int = 10000, min_df: int = 1, max_df: float = 1.0):
        """
        Initialize TF-IDF embedding service
        
        Args:
            max_features: Maximum number of features (vocabulary size)
            min_df: Minimum document frequency (absolute count)
            max_df: Maximum document frequency ratio (0.0-1.0)
        """
        self.max_features = max_features
        self.min_df = min_df
        self.max_df = max_df
        self._vectorizer: Optional[TfidfVectorizer] = None
        self._fitted = False
        
    @property
    def vectorizer(self) -> TfidfVectorizer:
        """Get or create the TF-IDF vectorizer"""
        if self._vectorizer is None:
            self._vectorizer = TfidfVectorizer(
                max_features=self.max_features,
                min_df=self.min_df,
                max_df=self.max_df,
                ngram_range=(1, 2),
                sublinear_tf=True,
                lowercase=True,
                analyzer='char_wb'  # Character n-grams for better Chinese support
            )
        return self._vectorizer
    
    def fit(self, documents: List[str]) -> 'TFidfEmbeddingService':
        """
        Fit the vectorizer on documents
        
        Args:
            documents: List of document texts
            
        Returns:
            self for chaining
        """
        logger.info(f"Fitting TF-IDF vectorizer on {len(documents)} documents")
        start_time = time.time()
        
        self.vectorizer.fit(documents)
        self._fitted = True
        
        fitting_time = time.time() - start_time
        logger.info(f"TF-IDF fitted in {fitting_time:.2f}s. Vocabulary size: {len(self.vectorizer.vocabulary_)}")
        
        return self
    
    def fit_transform(self, documents: List[str]) -> np.ndarray:
        """
        Fit vectorizer and transform documents to vectors
        
        Args:
            documents: List of document texts
            
        Returns:
            TF-IDF vectors as numpy array
        """
        self.fit(documents)
        return self.transform(documents)
    
    def transform(self, texts: List[str]) -> np.ndarray:
        """
        Transform texts to TF-IDF vectors
        
        Args:
            texts: List of text strings
            
        Returns:
            TF-IDF vectors as numpy array
        """
        if not texts:
            return np.array([])
        
        if not self._fitted:
            logger.warning("Vectorizer not fitted, fitting on provided texts")
            self.fit(texts)
        
        vectors = self.vectorizer.transform(texts)
        return vectors.toarray()
    
    def encode(self, texts: List[str], show_progress: bool = False) -> np.ndarray:
        """
        Encode texts to embeddings (alias for transform)
        
        Args:
            texts: List of text strings
            show_progress: Ignored for TF-IDF
            
        Returns:
            TF-IDF vectors as numpy array
        """
        return self.transform(texts)
    
    def encode_single(self, text: str) -> np.ndarray:
        """
        Encode a single text
        
        Args:
            text: Single text string
            
        Returns:
            TF-IDF vector as numpy array
        """
        return self.transform([text])[0]
    
    def search(self, query: str, documents: List[str], top_k: int = 5) -> List[Tuple[int, float]]:
        """
        Search for most similar documents
        
        Args:
            query: Query text
            documents: List of document texts
            top_k: Number of results to return
            
        Returns:
            List of (index, similarity_score) tuples
        """
        if not documents or not query:
            return []
        
        query_vec = self.encode_single(query)
        doc_vectors = self.transform(documents)
        
        similarities = cosine_similarity(query_vec.reshape(1, -1), doc_vectors)[0]
        
        # Get top-k indices
        indices = np.argsort(similarities)[::-1][:top_k]
        
        return [(int(idx), float(similarities[idx])) for idx in indices]
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the embedding service
        
        Returns:
            Dictionary with service information
        """
        return {
            "model_type": "TF-IDF",
            "max_features": self.max_features,
            "min_df": self.min_df,
            "max_df": self.max_df,
            "vocabulary_size": len(self.vectorizer.vocabulary_) if self._fitted else 0,
            "ngram_range": "(1, 2)",
            "analyzer": "char_wb"
        }
    
    def get_embedding_info(self) -> Dict[str, Any]:
        """
        Get embedding info (compatibility method for health checks)
        
        Returns:
            Dictionary with embedding information
        """
        return {
            "model_name": "TF-IDF",
            "dimension": self.max_features,
            "max_sequence_length": None,
            "model_type": "TFidfVectorizer"
        }
    
    def save(self, path: str) -> None:
        """
        Save vectorizer to file
        
        Args:
            path: File path to save
        """
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'wb') as f:
            pickle.dump({
                'vectorizer': self._vectorizer,
                'fitted': self._fitted,
                'max_features': self.max_features,
                'min_df': self.min_df,
                'max_df': self.max_df
            }, f)
        logger.info(f"TF-IDF vectorizer saved to {path}")
    
    @classmethod
    def load(cls, path: str) -> 'TFidfEmbeddingService':
        """
        Load vectorizer from file
        
        Args:
            path: File path to load from
            
        Returns:
            Loaded TF-IDF embedding service
        """
        with open(path, 'rb') as f:
            data = pickle.load(f)
        
        service = cls(
            max_features=data['max_features'],
            min_df=data['min_df'],
            max_df=data['max_df']
        )
        service._vectorizer = data['vectorizer']
        service._fitted = data['fitted']
        
        logger.info(f"TF-IDF vectorizer loaded from {path}")
        return service


# Singleton instance
embedding_service = TFidfEmbeddingService()
