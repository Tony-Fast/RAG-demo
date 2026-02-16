"""
Vector Store Service
Handles document storage and retrieval using TF-IDF + FAISS
"""

import os
import time
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import faiss
import pickle

from app.core.config import settings
from app.models.entities import DocumentChunk, SearchResult
from app.services.tfidf_embedding_service import embedding_service

logger = logging.getLogger(__name__)


class VectorStore:
    """
    FAISS-based vector store with TF-IDF embeddings for document retrieval
    """
    
    def __init__(self):
        self.index_path = Path(settings.VECTOR_STORE_PATH)
        self.index_path.mkdir(parents=True, exist_ok=True)
        
        self._embedding_dim = 0  # Will be set based on TF-IDF vocabulary
        self._index = None
        self._metadata = {}
        self._documents = {}  # Store document texts for TF-IDF search
        self._tfidf_fitted = False
        
    @property
    def index(self) -> faiss.Index:
        """
        Get or create FAISS index
        """
        if self._index is None:
            self._load_index()
        
        if self._index is None:
            self._create_index()
        
        return self._index
    
    def _create_index(self):
        """
        Create a new FAISS index
        """
        logger.info("Creating new FAISS index")
        
        # Use a fixed dimension for FAISS (TF-IDF vectors are sparse, we'll use a dense projection)
        self._embedding_dim = 512  # Fixed dimension for FAISS
        
        self._index = faiss.IndexFlatIP(self._embedding_dim)
        
        self._save_index()
    
    def _load_index(self) -> bool:
        """
        Load existing index from disk
        
        Returns:
            True if index was loaded, False otherwise
        """
        import os
        index_file = os.path.join(str(self.index_path), "index.faiss")
        metadata_file = os.path.join(str(self.index_path), "metadata.pkl")
        
        if not os.path.exists(index_file):
            logger.info("No existing index found")
            self._index = None
            self._metadata = {}
            self._documents = {}
            return False
        
        try:
            self._index = faiss.read_index(index_file)
            logger.info(f"Loaded FAISS index with {self._index.ntotal} vectors")
            
            if os.path.exists(metadata_file):
                with open(metadata_file, 'rb') as f:
                    data = pickle.load(f)
                    self._metadata = data.get('metadata', {})
                    self._documents = data.get('documents', {})
                    self._embedding_dim = data.get('embedding_dim', 512)
            
            logger.info(f"Loaded metadata for {len(self._metadata)} chunks")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load index: {e}")
            self._index = None
            self._metadata = {}
            self._documents = {}
            return False
    
    def _save_index(self):
        """
        Save index and metadata to disk (optional, graceful failure on Windows)
        """
        if self._index is None:
            return
        
        try:
            # Ensure directory exists
            import os
            os.makedirs(str(self.index_path), exist_ok=True)
            
            index_file = os.path.join(str(self.index_path), "index.faiss")
            metadata_file = os.path.join(str(self.index_path), "metadata.pkl")
            
            faiss.write_index(self._index, index_file)
            
            data = {
                'metadata': self._metadata,
                'documents': self._documents,
                'embedding_dim': self._embedding_dim
            }
            
            with open(metadata_file, 'wb') as f:
                pickle.dump(data, f)
            
            logger.info(f"Saved index ({self._index.ntotal} vectors) and metadata")
            
        except Exception as e:
            # Log but don't fail - in-memory storage works fine
            logger.warning(f"Could not save index to disk: {e}")
            logger.info("Using in-memory storage (data will be lost on restart)")
    
    def _create_dense_embedding(self, sparse_vector: np.ndarray) -> np.ndarray:
        """
        Create a fixed-size dense embedding from sparse TF-IDF vector
        
        Args:
            sparse_vector: TF-IDF sparse vector
            
        Returns:
            Dense vector of fixed size
        """
        # Convert sparse to dense and project to fixed dimension
        dense = np.asarray(sparse_vector).flatten()
        
        # Pad or truncate to fixed dimension
        if len(dense) < self._embedding_dim:
            dense = np.pad(dense, (0, self._embedding_dim - len(dense)))
        else:
            dense = dense[:self._embedding_dim]
        
        # L2 normalize
        norm = np.linalg.norm(dense)
        if norm > 0:
            dense = dense / norm
        
        return dense.astype('float32')
    
    def add_chunks(self, chunks: List[DocumentChunk], embeddings: np.ndarray, document_name: str = ""):
        """
        Add document chunks to the vector store
        
        Args:
            chunks: List of document chunks
            embeddings: Corresponding TF-IDF embeddings
            document_name: Name of the document for attribution
        """
        if not chunks or len(embeddings) == 0:
            logger.warning("No chunks or embeddings to add")
            return
        
        start_time = time.time()
        
        # Fit TF-IDF on all documents if not already fitted
        if not self._tfidf_fitted:
            all_texts = [chunk.content for chunk in chunks]
            embedding_service.fit(all_texts)
            self._tfidf_fitted = True
            logger.info("TF-IDF vectorizer fitted on new documents")
        
        # Ensure index is created FIRST with correct dimension
        if self._index is None:
            # Get the dimension from the first embedding
            first_dense = np.asarray(embeddings[0]).flatten()
            self._embedding_dim = max(len(first_dense), 1)  # Ensure at least 1
            self._create_index()
            logger.info(f"Created index with dimension {self._embedding_dim}")
        
        # Convert TF-IDF embeddings to dense FAISS vectors
        dense_embeddings = []
        for i, emb in enumerate(embeddings):
            dense = self._create_dense_embedding(emb)
            dense_embeddings.append(dense)
        
        dense_embeddings = np.array(dense_embeddings)
        
        # Generate IDs
        ids = np.array([self._generate_chunk_id(chunk) for chunk in chunks])
        
        # Add to FAISS index
        self._index.add(dense_embeddings)
        
        # Store metadata and documents
        for chunk in chunks:
            chunk_id = self._generate_chunk_id(chunk)
            self._metadata[str(chunk_id)] = {
                'document_id': chunk.document_id,
                'document_name': document_name or chunk.document_id,
                'chunk_index': chunk.chunk_index,
                'content': chunk.content,
                'metadata': chunk.metadata
            }
            self._documents[str(chunk_id)] = chunk.content
        
        # Try to save (but don't fail if it errors)
        try:
            self._save_index()
        except Exception as save_error:
            logger.warning(f"Index save skipped: {save_error}")
            logger.info("Continuing with in-memory storage only")
        
        elapsed = time.time() - start_time
        logger.info(f"Added {len(chunks)} chunks to index in {elapsed:.2f}s. Total vectors: {self._index.ntotal}")
    
    def _generate_chunk_id(self, chunk: DocumentChunk) -> int:
        """
        Generate a unique integer ID for a chunk
        
        Args:
            chunk: Document chunk
            
        Returns:
            Integer ID
        """
        import hashlib
        hash_input = f"{chunk.document_id}_{chunk.chunk_index}_{chunk.content[:100]}"
        hash_bytes = hashlib.md5(hash_input.encode()).digest()
        return int.from_bytes(hash_bytes[:4], 'big')
    
    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> List[SearchResult]:
        """
        Search for similar chunks
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            
        Returns:
            List of SearchResult objects
        """
        if self._index is None or self._index.ntotal == 0:
            logger.warning("Index is empty or not initialized")
            return []
        
        # Convert query to dense and normalize
        query_dense = self._create_dense_embedding(query_embedding).reshape(1, -1)
        
        # Search
        scores, indices = self._index.search(query_dense, top_k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue
            
            chunk_id = str(idx)
            metadata = self._metadata.get(chunk_id)
            
            if metadata:
                result = SearchResult(
                    chunk_id=chunk_id,
                    document_id=metadata['document_id'],
                    document_name="",
                    chunk_index=metadata['chunk_index'],
                    content=metadata['content'],
                    similarity_score=float(score),
                    metadata=metadata.get('metadata', {})
                )
                results.append(result)
        
        return results
    
    def search_by_text(self, query_text: str, top_k: int = 5) -> List[SearchResult]:
        """
        Search by text query using TF-IDF
        
        Args:
            query_text: Text to search for
            top_k: Number of results
            
        Returns:
            List of SearchResult objects
        """
        # Use TF-IDF service for text-based search
        if not self._documents:
            return []
        
        # Get all stored documents
        doc_ids = list(self._documents.keys())
        doc_texts = [self._documents[doc_id] for doc_id in doc_ids]
        
        # Search using TF-IDF
        results = embedding_service.search(query_text, doc_texts, top_k)
        
        search_results = []
        for doc_idx, score in results:
            chunk_id = doc_ids[doc_idx]
            metadata = self._metadata.get(chunk_id)
            
            if metadata:
                search_results.append(SearchResult(
                    chunk_id=chunk_id,
                    document_id=metadata['document_id'],
                    document_name=metadata.get('document_name', ''),
                    chunk_index=metadata['chunk_index'],
                    content=metadata['content'],
                    similarity_score=score,
                    metadata=metadata.get('metadata', {})
                ))
        
        logger.info(f"Text search returned {len(search_results)} results")
        return search_results
    
    def delete_by_document_id(self, document_id: str) -> int:
        """
        Delete all chunks belonging to a document
        
        Args:
            document_id: Document ID to delete
            
        Returns:
            Number of chunks deleted
        """
        if self._index is None:
            return 0
        
        deleted_count = 0
        ids_to_delete = []
        
        for chunk_id, metadata in list(self._metadata.items()):
            if metadata.get('document_id') == document_id:
                ids_to_delete.append(int(chunk_id))
                deleted_count += 1
        
        if ids_to_delete:
            self._remove_ids(ids_to_delete)
            logger.info(f"Deleted {deleted_count} chunks for document {document_id}")
        
        return deleted_count
    
    def _remove_ids(self, ids: List[int]):
        """
        Remove IDs from index by rebuilding
        
        Args:
            ids: List of IDs to remove
        """
        if not ids or self._index is None:
            return
        
        id_set = set(ids)
        
        all_ids = list(range(self._index.ntotal))
        keep_ids = [id for id in all_ids if id not in id_set]
        
        if not keep_ids:
            self._create_index()
            self._metadata = {}
            self._documents = {}
            return
        
        embeddings = self._index.reconstruct_n(0, len(all_ids))
        keep_embeddings = [embeddings[i] for i in range(len(all_ids)) if all_ids[i] not in id_set]
        
        self._index = faiss.IndexFlatIP(self._embedding_dim)
        if keep_embeddings:
            self._index.add(np.array(keep_embeddings))
        
        self._metadata = {
            chunk_id: meta 
            for chunk_id, meta in self._metadata.items() 
            if int(chunk_id) not in id_set
        }
        
        self._documents = {
            chunk_id: content
            for chunk_id, content in self._documents.items()
            if int(chunk_id) not in id_set
        }
        
        self._save_index()
    
    def clear(self):
        """
        Clear all data from the vector store
        """
        self._create_index()
        self._metadata = {}
        self._documents = {}
        self._tfidf_fitted = False
        self._save_index()
        logger.info("Vector store cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get vector store statistics
        
        Returns:
            Dictionary with statistics
        """
        return {
            "total_vectors": self._index.ntotal if self._index else 0,
            "dimension": self._embedding_dim,
            "index_type": "FlatIP",
            "metadata_count": len(self._metadata),
            "documents_count": len(set(
                meta.get('document_id') for meta in self._metadata.values()
            )) if self._metadata else 0
        }
    
    def rebuild_index(self, chunks: List[DocumentChunk] = None):
        """
        Rebuild the entire index
        
        Args:
            chunks: Optional list of chunks to rebuild with
        """
        logger.info("Rebuilding vector index...")
        
        self._create_index()
        self._metadata = {}
        self._documents = {}
        self._tfidf_fitted = False
        
        if chunks:
            all_texts = [chunk.content for chunk in chunks]
            embedding_service.fit(all_texts)
            self._tfidf_fitted = True
            
            embeddings = embedding_service.encode(all_texts)
            self.add_chunks(chunks, embeddings)
        
        logger.info("Index rebuild complete")


# Singleton instance
vector_store = VectorStore()
