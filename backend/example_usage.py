#!/usr/bin/env python
"""
VoxDocs Backend - Complete Example Usage Script
Demonstrates all API features including:
- Document upload & management
- Session management & chat history  
- Question answering with persistence
- Speech-to-text & text-to-speech
- Document statistics
"""

import requests
import json
from pathlib import Path
import time
from typing import Optional, Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
HEALTH_CHECK_URL = "http://localhost:8000/health"

# Sample files
SAMPLE_PDF_PATH = "sample.pdf"
SAMPLE_AUDIO_PATH = "sample.mp3"

# Colors for output
GREEN = "\033[92m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"


def print_success(msg: str):
    """Print success message"""
    print(f"{GREEN}✓{RESET} {msg}")


def print_error(msg: str):
    """Print error message"""
    print(f"{RED}✗{RESET} {msg}")


def print_info(msg: str):
    """Print info message"""
    print(f"{BLUE}ℹ{RESET} {msg}")


def print_section(title: str):
    """Print section header"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{title:^60}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")


# ==================== Health & Status ====================

def check_api_health() -> bool:
    """Check if API is running"""
    try:
        response = requests.get(HEALTH_CHECK_URL, timeout=5)
        health = response.json()
        print_success(f"API is healthy - v{health.get('version')}")
        return True
    except Exception as e:
        print_error(f"API not running: {e}")
        return False


# ==================== Document Management ====================

def upload_document(pdf_path: str) -> Optional[dict]:
    """Upload a PDF document"""
    print_info(f"Uploading document: {pdf_path}")
    
    try:
        with open(pdf_path, "rb") as f:
            files = {"file": (Path(pdf_path).name, f, "application/pdf")}
            response = requests.post(
                f"{API_BASE_URL}/upload",
                files=files,
                timeout=60
            )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Document uploaded successfully!")
            print(f"  Filename: {data['filename']}")
            print(f"  Chunks: {data['chunks_created']}")
            return data
        else:
            print_error(f"Upload failed: {response.text}")
            return None
    except FileNotFoundError:
        print_error(f"File not found: {pdf_path}")
        return None
    except Exception as e:
        print_error(f"Error uploading: {e}")
        return None


def get_all_documents() -> Optional[list]:
    """Get list of all uploaded documents"""
    print_info("Retrieving all documents...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/documents", timeout=10)
        
        if response.status_code == 200:
            documents = response.json()
            if documents:
                print_success(f"Found {len(documents)} document(s)")
                for doc in documents:
                    print(f"  - {doc['filename']} ({doc['chunk_count']} chunks)")
            else:
                print_info("No documents uploaded yet")
            return documents
        else:
            print_error(f"Failed to get documents: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error retrieving documents: {e}")
        return None


def get_document_stats() -> Optional[dict]:
    """Get document statistics"""
    print_info("Retrieving document statistics...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/documents/stats/overview", timeout=10)
        
        if response.status_code == 200:
            stats = response.json()
            print_success("Document statistics:")
            print(f"  Total documents: {stats['total_documents']}")
            print(f"  Total chunks: {stats['total_chunks']}")
            print(f"  Total embeddings: {stats['total_embeddings']}")
            print(f"  Total size: {stats['total_size_bytes'] / 1024 / 1024:.2f} MB")
            return stats
        else:
            print_error(f"Failed to get stats: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error retrieving stats: {e}")
        return None


# ==================== Session Management ====================

def create_session(title: Optional[str] = None) -> Optional[str]:
    """Create a new chat session"""
    title = title or "New Conversation"
    print_info(f"Creating session: '{title}'")
    
    try:
        payload = {"title": title}
        response = requests.post(
            f"{API_BASE_URL}/session/new",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            session = response.json()
            session_id = session["id"]
            print_success(f"Session created: {session_id}")
            return session_id
        else:
            print_error(f"Failed to create session: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error creating session: {e}")
        return None


def get_all_sessions() -> Optional[list]:
    """Get list of all chat sessions"""
    print_info("Retrieving all sessions...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/session", timeout=10)
        
        if response.status_code == 200:
            sessions = response.json()
            if sessions:
                print_success(f"Found {len(sessions)} session(s)")
                for session in sessions:
                    print(f"  - {session['title']}")
                    print(f"    ID: {session['id']}")
            else:
                print_info("No sessions yet")
            return sessions
        else:
            print_error(f"Failed to get sessions: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error retrieving sessions: {e}")
        return None


def get_session_history(session_id: str) -> Optional[dict]:
    """Get chat history for a session"""
    print_info(f"Retrieving history for session: {session_id}")
    
    try:
        response = requests.get(f"{API_BASE_URL}/session/{session_id}", timeout=10)
        
        if response.status_code == 200:
            history = response.json()
            session = history["session"]
            messages = history["messages"]
            
            print_success(f"Session: {session['title']}")
            print(f"  Messages: {len(messages)}")
            
            if messages:
                print("\n  Chat History:")
                for i, msg in enumerate(messages, 1):
                    print(f"\n    Q{i}: {msg['question']}")
                    print(f"    A{i}: {msg['answer'][:100]}...")
                    print(f"    Confidence: {msg['confidence']:.0%}")
            else:
                print_info("  No messages yet")
            
            return history
        else:
            print_error(f"Failed to get history: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error retrieving history: {e}")
        return None


def delete_session(session_id: str) -> bool:
    """Delete a session"""
    print_info(f"Deleting session: {session_id}")
    
    try:
        response = requests.delete(f"{API_BASE_URL}/session/{session_id}", timeout=10)
        
        if response.status_code == 200:
            print_success(f"Session deleted")
            return True
        else:
            print_error(f"Failed to delete session: {response.text}")
            return False
    except Exception as e:
        print_error(f"Error deleting session: {e}")
        return False


# ==================== Question Answering ====================

def ask_question(question: str, include_audio: bool = False) -> Optional[dict]:
    """Ask a question about documents (without session)"""
    print_info(f"Asking: {question}")
    
    try:
        payload = {
            "question": question,
            "include_audio": include_audio
        }
        response = requests.post(
            f"{API_BASE_URL}/ask",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Answer received!")
            print(f"  Answer: {data['answer'][:100]}...")
            print(f"  Confidence: {data['confidence']:.0%}")
            if data.get('sources'):
                print(f"  Sources: {', '.join(data['sources'])}")
            return data
        else:
            print_error(f"Query failed: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error asking question: {e}")
        return None


def ask_question_with_session(
    session_id: str,
    question: str,
    include_audio: bool = False
) -> Optional[dict]:
    """Ask a question with session context"""
    print_info(f"Asking in session: {question}")
    
    try:
        payload = {
            "session_id": session_id,
            "question": question,
            "include_audio": include_audio
        }
        response = requests.post(
            f"{API_BASE_URL}/ask/session",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Answer received and saved!")
            print(f"  Answer: {data['answer'][:100]}...")
            print(f"  Confidence: {data['confidence']:.0%}")
            return data
        elif response.status_code == 404:
            print_error(f"Session not found")
            return None
        else:
            print_error(f"Query failed: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error asking question: {e}")
        return None


# ==================== Speech Features ====================

def speech_to_text(audio_path: str) -> Optional[dict]:
    """Convert speech to text"""
    print_info(f"Transcribing: {audio_path}")
    
    try:
        with open(audio_path, "rb") as f:
            files = {"file": (Path(audio_path).name, f, "audio/mpeg")}
            response = requests.post(
                f"{API_BASE_URL}/voice/speech-to-text",
                files=files,
                timeout=60
            )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Transcription successful!")
            print(f"  Text: {data['text']}")
            print(f"  Duration: {data['duration']:.2f}s")
            return data
        else:
            print_error(f"Transcription failed: {response.text}")
            return None
    except FileNotFoundError:
        print_error(f"File not found: {audio_path}")
        return None
    except Exception as e:
        print_error(f"Error transcribing: {e}")
        return None


def text_to_speech(text: str) -> Optional[dict]:
    """Convert text to speech"""
    print_info(f"Creating speech: {text[:50]}...")
    
    try:
        payload = {"text": text}
        response = requests.post(
            f"{API_BASE_URL}/voice/text-to-speech",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Speech created!")
            print(f"  Audio URL: {data['audio_url']}")
            print(f"  Duration: {data['duration']:.2f}s")
            return data
        else:
            print_error(f"Speech creation failed: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error creating speech: {e}")
        return None


def get_upload_status() -> Optional[dict]:
    """Get status of uploads and vector store"""
    print_info("Checking API status...")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/upload/status",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            doc_stats = data.get('statistics', {}).get('documents', {})
            vector_stats = data.get('statistics', {}).get('vector_store', {})
            
            print_success("Status retrieved!")
            print("\n  Documents:")
            print(f"    Total: {doc_stats.get('total_documents', 0)}")
            print(f"    Size: {doc_stats.get('total_size_bytes', 0) / 1024 / 1024:.2f} MB")
            print(f"    Chunks: {doc_stats.get('total_chunks', 0)}")
            
            print("\n  Vector Store:")
            print(f"    Vectors: {vector_stats.get('total_vectors', 0)}")
            print(f"    Metadata: {vector_stats.get('metadata_count', 0)}")
            return data
        else:
            print_error(f"Status check failed: {response.text}")
            return None
    except Exception as e:
        print_error(f"Error checking status: {e}")
        return None


# ==================== Demo Workflows ====================

def demo_basic_qna():
    """Demo: Basic question answering without sessions"""
    print_section("Demo: Basic Q&A (No Sessions)")
    
    print_info("This demonstrates asking questions without using sessions")
    print_info("Useful for one-off queries without persistence\n")
    
    ask_question("What are the main features?")
    ask_question("Can you provide a summary?")


def demo_session_workflow():
    """Demo: Complete session-based conversation workflow"""
    print_section("Demo: Session-Based Conversation")
    
    print_info("This demonstrates creating a session and maintaining conversation history\n")
    
    # 1. Create session
    session_id = create_session("Cloud Computing Questions")
    if not session_id:
        return
    
    time.sleep(1)
    
    # 2. Ask multiple questions in context
    print_info("\nAsking questions in session context...\n")
    ask_question_with_session(session_id, "What is cloud computing?")
    time.sleep(0.5)
    
    ask_question_with_session(session_id, "What are the main benefits?")
    time.sleep(0.5)
    
    ask_question_with_session(session_id, "How does it differ from on-premise?")
    time.sleep(1)
    
    # 3. View conversation history
    get_session_history(session_id)
    
    # 4. Optionally delete
    # delete_session(session_id)


def demo_document_management():
    """Demo: Document upload and management"""
    print_section("Demo: Document Management")
    
    print_info("This demonstrates uploading documents and viewing their metadata\n")
    
    # Get all documents
    get_all_documents()
    time.sleep(0.5)
    
    # Get document stats
    get_document_stats()


def demo_session_list():
    """Demo: List and manage sessions"""
    print_section("Demo: Session Management")
    
    print_info("This demonstrates listing sessions and accessing their history\n")
    
    # Get all sessions
    sessions = get_all_sessions()
    
    if sessions and len(sessions) > 0:
        time.sleep(0.5)
        # Get history of first session
        first_session_id = sessions[0]["id"]
        get_session_history(first_session_id)


def demo_complete_workflow():
    """Demo: Complete workflow end-to-end"""
    print_section("Demo: Complete Workflow")
    
    print_info("This demonstrates the entire system from upload to Q&A with sessions\n")
    
    # Check health
    if not check_api_health():
        print_error("API is not running. Start it with:")
        print("  python -m uvicorn app.main:app --reload")
        return
    
    time.sleep(1)
    
    # Get document stats
    get_document_stats()
    time.sleep(0.5)
    
    # Create a session
    print("\n")
    session_id = create_session("API Testing Session")
    if not session_id:
        return
    
    time.sleep(1)
    
    # Ask questions with session
    print("\n")
    ask_question_with_session(session_id, "What documents are available?")
    time.sleep(0.5)
    
    ask_question_with_session(session_id, "Tell me about the features")
    time.sleep(1)
    
    # View all sessions
    print("\n")
    get_all_sessions()
    time.sleep(0.5)
    
    # View session history
    print("\n")
    get_session_history(session_id)
    
    print_section("Demo Complete!")
    print(f"{GREEN}✨ All features demonstrated successfully!{RESET}")
    print(f"\n📚 API Documentation: {BLUE}http://localhost:8000/docs{RESET}")
    print(f"📝 MongoDB data stored in: {BLUE}MongoDB Atlas{RESET}")
    print(f"📊 View data at: {BLUE}https://cloud.mongodb.com{RESET}")


# ==================== Main ====================

def main():
    """Main entry point"""
    print_section("VoxDocs Backend - Example Usage")
    
    print(f"API Base URL: {BLUE}{API_BASE_URL}{RESET}")
    print(f"Health Check: {BLUE}{HEALTH_CHECK_URL}{RESET}\n")
    
    # Menu
    print("Select a demo:")
    print("  1. Basic Q&A (no sessions)")
    print("  2. Session-based conversation")
    print("  3. Document management")
    print("  4. Session management")
    print("  5. Complete workflow (recommended)")
    print("  6. API health check only")
    print("  0. Exit")
    
    while True:
        try:
            choice = input(f"\n{BLUE}Enter choice (0-6):{RESET} ").strip()
            
            if choice == "0":
                print("Goodbye!")
                break
            elif choice == "1":
                demo_basic_qna()
            elif choice == "2":
                demo_session_workflow()
            elif choice == "3":
                demo_document_management()
            elif choice == "4":
                demo_session_list()
            elif choice == "5":
                demo_complete_workflow()
            elif choice == "6":
                check_api_health()
            else:
                print_error("Invalid choice")
        except KeyboardInterrupt:
            print("\nInterrupted by user")
            break
        except Exception as e:
            print_error(f"Error: {e}")


if __name__ == "__main__":
    main()
