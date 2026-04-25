"""
Document management service.
Tracks uploaded documents and their processing status.
"""
import logging
from typing import List
from datetime import datetime
from app.db.models import Document

logger = logging.getLogger(__name__)


class DocumentService:
    """
    Manages document metadata and tracking.
    """

    async def register_document(
        self,
        filename: str,
        file_path: str,
        chunk_count: int,
        file_size: int,
        embedding_count: int = 0
    ) -> Document:
        """
        Register an uploaded document in the database.
        
        Args:
            filename: Original filename
            file_path: Path to stored file
            chunk_count: Number of text chunks
            file_size: File size in bytes
            embedding_count: Number of embeddings created
            
        Returns:
            Created Document document
        """
        try:
            logger.info(f"Registering document: {filename}")
            
            doc = Document(
                filename=filename,
                file_path=file_path,
                uploaded_at=datetime.utcnow(),
                chunk_count=chunk_count,
                file_size=file_size,
                status="success",
                embedding_count=embedding_count
            )
            
            await doc.save()
            logger.info(f"Document registered: {doc.id}")
            
            return doc
            
        except Exception as e:
            logger.error(f"Error registering document: {str(e)}")
            raise

    async def get_all_documents(self) -> List[Document]:
        """
        Retrieve all uploaded documents.
        
        Returns:
            List of Document documents, sorted by upload time (newest first)
        """
        try:
            documents = await Document.find_all().sort(
                [("uploaded_at", -1)]
            ).to_list()
            
            logger.info(f"Retrieved {len(documents)} documents")
            return documents
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            raise

    async def get_document(self, doc_id: str) -> Document:
        """
        Retrieve a specific document by ID.
        
        Args:
            doc_id: Document ID
            
        Returns:
            Document document
            
        Raises:
            ValueError: If document not found
        """
        try:
            from bson import ObjectId
            
            obj_id = ObjectId(doc_id) if isinstance(doc_id, str) else doc_id
            doc = await Document.get(obj_id)
            
            if not doc:
                raise ValueError(f"Document {doc_id} not found")
            
            logger.info(f"Retrieved document: {doc_id}")
            return doc
            
        except Exception as e:
            logger.error(f"Error retrieving document: {str(e)}")
            raise

    async def get_documents_count(self) -> int:
        """
        Get total count of uploaded documents.
        
        Returns:
            Number of documents
        """
        try:
            count = await Document.find_all().count()
            logger.info(f"Total documents: {count}")
            return count
            
        except Exception as e:
            logger.error(f"Error counting documents: {str(e)}")
            raise

    async def get_document_stats(self) -> dict:
        """
        Get statistics about uploaded documents.
        
        Returns:
            Dictionary with statistics
        """
        try:
            documents = await self.get_all_documents()
            
            total_size = sum(doc.file_size for doc in documents)
            total_chunks = sum(doc.chunk_count for doc in documents)
            total_embeddings = sum(doc.embedding_count for doc in documents)
            
            stats = {
                "total_documents": len(documents),
                "total_size_bytes": total_size,
                "total_chunks": total_chunks,
                "total_embeddings": total_embeddings,
                "average_file_size": total_size / len(documents) if documents else 0,
                "average_chunks_per_doc": total_chunks / len(documents) if documents else 0
            }
            
            logger.info(f"Document stats: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error getting document stats: {str(e)}")
            raise
