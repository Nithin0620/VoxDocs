"""
RAG (Retrieval-Augmented Generation) service.
Orchestrates document retrieval and LLM-based answer generation.
"""
import logging
from typing import List, Tuple, Optional
from app.utils.embeddings import EmbeddingGenerator, FAISSVectorStore
from app.utils.file_loader import PDFLoader, TextChunker
from pathlib import Path

logger = logging.getLogger(__name__)


class RAGService:
    """
    Retrieval-Augmented Generation service.
    Handles document upload, embedding, and query processing.
    """

    def __init__(
        self,
        openai_api_key: str,
        faiss_index_path: Path,
        faiss_metadata_path: Path,
        embedding_model: str = "text-embedding-3-small",
        llm_model: str = "gpt-3.5-turbo",
        chunk_size: int = 1000,
        chunk_overlap: int = 100,
        top_k: int = 3
    ):
        """
        Initialize RAG service.
        
        Args:
            openai_api_key: OpenAI API key
            faiss_index_path: Path to FAISS index
            faiss_metadata_path: Path to FAISS metadata
            embedding_model: Model for embeddings
            llm_model: Model for LLM responses
            chunk_size: Size of document chunks
            chunk_overlap: Overlap between chunks
            top_k: Number of documents to retrieve
        """
        self.embedding_generator = EmbeddingGenerator(openai_api_key, embedding_model)
        self.vector_store = FAISSVectorStore(faiss_index_path, faiss_metadata_path)
        self.llm_model = llm_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.top_k = top_k
        self.openai_api_key = openai_api_key
        self._llm_client = None

    @property
    def llm_client(self):
        """Lazy-load OpenAI client for LLM."""
        if self._llm_client is None:
            try:
                from openai import OpenAI
                self._llm_client = OpenAI(api_key=self.openai_api_key)
            except ImportError:
                raise ImportError("openai package not installed")
        return self._llm_client

    async def process_document(self, file_path: Path, filename: str) -> dict:
        """
        Process a PDF document and add to vector store.
        
        Args:
            file_path: Path to the uploaded file
            filename: Original filename
            
        Returns:
            Processing result with chunk count
        """
        try:
            # Extract text from PDF
            logger.info(f"Extracting text from {filename}")
            text = PDFLoader.extract_text_from_pdf(str(file_path))

            if not text.strip():
                raise ValueError("PDF contains no extractable text")

            # Chunk text
            logger.info(f"Chunking document: {filename}")
            chunks_with_metadata = TextChunker.chunk_with_metadata(
                text,
                filename,
                self.chunk_size,
                self.chunk_overlap
            )

            # Generate embeddings
            logger.info(f"Generating embeddings for {len(chunks_with_metadata)} chunks")
            chunk_texts = [chunk[0] for chunk in chunks_with_metadata]
            embeddings = self.embedding_generator.generate_embeddings_batch(chunk_texts)

            # Extract metadata
            metadata_list = [chunk[1] for chunk in chunks_with_metadata]

            # Add to vector store
            self.vector_store.add_embeddings(embeddings, metadata_list)

            logger.info(f"Successfully processed {filename}")
            return {
                "filename": filename,
                "chunks_created": len(chunks_with_metadata),
                "success": True
            }

        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            raise

    async def query(self, question: str) -> Tuple[str, List[str], float]:
        """
        Query documents and generate an answer using LLM.
        
        Args:
            question: User's question
            
        Returns:
            Tuple of (answer, sources, confidence_score)
        """
        try:
            # Generate embedding for question
            logger.info(f"Processing question: {question}")
            question_embedding = self.embedding_generator.generate_embedding(question)

            # Retrieve relevant documents
            search_results = self.vector_store.search(question_embedding, self.top_k)

            if not search_results:
                return "No relevant documents found.", [], 0.0

            # Extract chunks and metadata
            relevant_chunks = [item[0]["source"] for item in search_results]
            context = "\n---\n".join([
                f"Source: {item[0]['source']}\n{item[0]}"
                for item, _ in search_results
            ])

            # Generate answer using LLM
            logger.info("Generating answer with LLM")
            answer = self._generate_answer_with_llm(question, context)

            # Calculate confidence (inverse of average distance)
            distances = [distance for _, distance in search_results]
            avg_distance = sum(distances) / len(distances)
            # Normalize: closer distance = higher confidence
            confidence = max(0.0, 1 - (avg_distance / 100))

            logger.info(f"Generated answer with confidence: {confidence:.2f}")
            return answer, relevant_chunks, confidence

        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            raise

    def _generate_answer_with_llm(self, question: str, context: str) -> str:
        """
        Generate answer using OpenAI LLM.
        
        Args:
            question: User's question
            context: Retrieved context from documents
            
        Returns:
            Generated answer
        """
        try:
            prompt = f"""Based on the following document context, answer the question concisely and accurately.

Context:
{context}

Question: {question}

Answer:"""

            response = self.llm_client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on provided documents."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Error generating answer with LLM: {str(e)}")
            raise

    def get_statistics(self) -> dict:
        """Get RAG service statistics."""
        return {
            "vector_store": self.vector_store.get_stats(),
            "embedding_model": "text-embedding-3-small",
            "llm_model": self.llm_model
        }
