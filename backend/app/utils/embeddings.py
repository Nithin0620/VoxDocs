"""
Embedding generation and vector store management.
Handles integration with OpenAI embeddings and FAISS.
"""
import json
import logging
from typing import List, Tuple, Optional
from pathlib import Path
import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """
    Generates embeddings using OpenAI API.
    """

    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        """
        Initialize embedding generator.
        
        Args:
            api_key: OpenAI API key
            model: Embedding model name
        """
        self.api_key = api_key
        self.model = model
        self._client = None

    @property
    def client(self):
        """Lazy-load OpenAI client."""
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("openai package not installed. Install with: pip install openai")
        return self._client

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        try:
            response = self.client.embeddings.create(
                input=[text],
                model=self.model
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise

    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batches.
        
        Args:
            texts: List of texts to embed
            batch_size: Number of texts per API call
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            try:
                response = self.client.embeddings.create(
                    input=batch,
                    model=self.model
                )
                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)
                logger.info(f"Generated embeddings for batch {i//batch_size + 1}")
            except Exception as e:
                logger.error(f"Error in batch embedding: {str(e)}")
                raise

        return embeddings


class FAISSVectorStore:
    """
    Manages FAISS vector store for efficient similarity search.
    Stores embeddings and metadata for retrieval.
    """

    def __init__(self, index_path: Path, metadata_path: Path, embedding_dim: int = 1536):
        """
        Initialize FAISS vector store.
        
        Args:
            index_path: Path to save/load FAISS index
            metadata_path: Path to save/load metadata
            embedding_dim: Dimension of embeddings
        """
        self.index_path = Path(index_path)
        self.metadata_path = Path(metadata_path)
        self.embedding_dim = embedding_dim
        self.index = None
        self.metadata = []
        self._load_index()

    def _load_index(self):
        """Load existing FAISS index and metadata if available."""
        try:
            import faiss
            if self.index_path.exists():
                self.index = faiss.read_index(str(self.index_path))
                logger.info("Loaded existing FAISS index")
            else:
                self.index = faiss.IndexFlatL2(self.embedding_dim)
                logger.info("Created new FAISS index")

            if self.metadata_path.exists():
                with open(self.metadata_path, "r") as f:
                    self.metadata = json.load(f)
        except ImportError:
            raise ImportError("faiss-cpu package not installed. Install with: pip install faiss-cpu")
        except Exception as e:
            logger.error(f"Error loading index: {str(e)}")
            raise

    def add_embeddings(self, embeddings: List[List[float]], metadata: List[dict]) -> None:
        """
        Add embeddings to the vector store.
        
        Args:
            embeddings: List of embedding vectors
            metadata: List of metadata dicts corresponding to embeddings
        """
        try:
            import faiss
            
            # Convert to numpy array
            embeddings_array = np.array(embeddings, dtype="float32")
            
            # Add to index
            self.index.add(embeddings_array)
            self.metadata.extend(metadata)
            
            # Save
            self._save_index()
            logger.info(f"Added {len(embeddings)} embeddings to FAISS index")
        except Exception as e:
            logger.error(f"Error adding embeddings: {str(e)}")
            raise

    def search(self, query_embedding: List[float], k: int = 3) -> List[Tuple[str, float]]:
        """
        Search for similar embeddings.
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            
        Returns:
            List of (text, distance) tuples
        """
        try:
            # Ensure we don't search for more results than available
            k = min(k, len(self.metadata))
            
            if k == 0:
                return []

            query_array = np.array([query_embedding], dtype="float32")
            distances, indices = self.index.search(query_array, k)

            results = []
            for distance, idx in zip(distances[0], indices[0]):
                if idx != -1:  # -1 means invalid result
                    results.append((self.metadata[idx], float(distance)))

            return results
        except Exception as e:
            logger.error(f"Error searching index: {str(e)}")
            raise

    def _save_index(self) -> None:
        """Save FAISS index and metadata to disk."""
        try:
            import faiss
            self.index_path.parent.mkdir(parents=True, exist_ok=True)
            self.metadata_path.parent.mkdir(parents=True, exist_ok=True)

            faiss.write_index(self.index, str(self.index_path))

            with open(self.metadata_path, "w") as f:
                json.dump(self.metadata, f)

            logger.info("FAISS index and metadata saved")
        except Exception as e:
            logger.error(f"Error saving index: {str(e)}")
            raise

    def get_stats(self) -> dict:
        """Get vector store statistics."""
        return {
            "total_vectors": self.index.ntotal if self.index else 0,
            "embedding_dim": self.embedding_dim,
            "metadata_count": len(self.metadata)
        }
