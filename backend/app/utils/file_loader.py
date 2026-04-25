"""
PDF file loading and text extraction utilities.
Handles document processing and chunking for RAG pipeline.
"""
import logging
from typing import List, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class PDFLoader:
    """
    Loads and extracts text from PDF files.
    Requires PyPDF2 or pdfplumber.
    """

    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """
        Extract text from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text from the PDF
            
        Raises:
            ValueError: If file cannot be read
        """
        try:
            import pdfplumber
        except ImportError:
            logger.error("pdfplumber not installed. Install with: pip install pdfplumber")
            raise ImportError("pdfplumber is required for PDF extraction")

        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
                    text += "\n"
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")

        return text.strip()

    @staticmethod
    def validate_pdf_file(file_path: str) -> bool:
        """
        Validate that the file is a valid PDF.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file is a valid PDF, False otherwise
        """
        try:
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                return len(pdf.pages) > 0
        except Exception:
            return False


class TextChunker:
    """
    Splits text into overlapping chunks for embedding.
    Preserves context with configurable overlap.
    """

    @staticmethod
    def chunk_text(
        text: str,
        chunk_size: int = 1000,
        overlap: int = 100
    ) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to split
            chunk_size: Number of characters per chunk
            overlap: Number of overlapping characters between chunks
            
        Returns:
            List of text chunks
        """
        if not text:
            return []

        chunks = []
        start = 0

        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk = text[start:end]

            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind(".")
                if last_period != -1 and last_period > chunk_size * 0.7:
                    end = start + last_period + 1
                    chunk = text[start:end]

            chunks.append(chunk.strip())
            start = end - overlap

        logger.info(f"Created {len(chunks)} chunks from text")
        return chunks

    @staticmethod
    def chunk_with_metadata(
        text: str,
        filename: str,
        chunk_size: int = 1000,
        overlap: int = 100
    ) -> List[Tuple[str, dict]]:
        """
        Split text into chunks with metadata.
        
        Args:
            text: Text to split
            filename: Source document filename
            chunk_size: Number of characters per chunk
            overlap: Number of overlapping characters between chunks
            
        Returns:
            List of (chunk_text, metadata) tuples
        """
        chunks = TextChunker.chunk_text(text, chunk_size, overlap)
        
        return [
            (chunk, {
                "source": filename,
                "chunk_index": i,
                "total_chunks": len(chunks)
            })
            for i, chunk in enumerate(chunks)
        ]
