#!/usr/bin/env python
"""
VoxDocs Backend - Example Usage Script
Demonstrates how to use the API programmatically
"""

import requests
import json
from pathlib import Path
import time

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
HEALTH_CHECK_URL = "http://localhost:8000/health"

# Sample PDF path (you need to download or create one)
SAMPLE_PDF_PATH = "sample.pdf"
SAMPLE_AUDIO_PATH = "sample.mp3"


def check_api_health():
    """Check if API is running"""
    try:
        response = requests.get(HEALTH_CHECK_URL, timeout=5)
        print(f"✓ API Health: {response.json()}")
        return True
    except Exception as e:
        print(f"✗ API not running: {e}")
        return False


def upload_document(pdf_path: str) -> dict:
    """Upload a PDF document"""
    print(f"\n📄 Uploading document: {pdf_path}")
    
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
            print(f"✓ Upload successful!")
            print(f"  - Chunks created: {data['chunks_created']}")
            print(f"  - Filename: {data['filename']}")
            return data
        else:
            print(f"✗ Upload failed: {response.text}")
            return None
    except FileNotFoundError:
        print(f"✗ File not found: {pdf_path}")
        return None
    except Exception as e:
        print(f"✗ Error uploading: {e}")
        return None


def ask_question(question: str, include_audio: bool = False) -> dict:
    """Ask a question about the document"""
    print(f"\n❓ Asking: {question}")
    
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
            print(f"✓ Answer received!")
            print(f"  - Answer: {data['answer'][:100]}...")
            print(f"  - Confidence: {data['confidence']:.2%}")
            print(f"  - Sources: {', '.join(data['sources'])}")
            if data.get('audio_url'):
                print(f"  - Audio: {data['audio_url']}")
            return data
        else:
            print(f"✗ Query failed: {response.text}")
            return None
    except Exception as e:
        print(f"✗ Error asking question: {e}")
        return None


def speech_to_text(audio_path: str) -> dict:
    """Convert speech to text"""
    print(f"\n🎙️  Transcribing: {audio_path}")
    
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
            print(f"✓ Transcription successful!")
            print(f"  - Text: {data['text']}")
            print(f"  - Duration: {data['duration']:.2f}s")
            return data
        else:
            print(f"✗ Transcription failed: {response.text}")
            return None
    except FileNotFoundError:
        print(f"✗ File not found: {audio_path}")
        return None
    except Exception as e:
        print(f"✗ Error transcribing: {e}")
        return None


def text_to_speech(text: str) -> dict:
    """Convert text to speech"""
    print(f"\n🔊 Creating speech: {text[:50]}...")
    
    try:
        payload = {"text": text}
        response = requests.post(
            f"{API_BASE_URL}/voice/text-to-speech",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Speech created!")
            print(f"  - Audio URL: {data['audio_url']}")
            print(f"  - Duration: {data['duration']:.2f}s")
            return data
        else:
            print(f"✗ Speech creation failed: {response.text}")
            return None
    except Exception as e:
        print(f"✗ Error creating speech: {e}")
        return None


def get_upload_status() -> dict:
    """Get status of uploads and vector store"""
    print("\n📊 Checking status...")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/upload/status",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            stats = data.get('statistics', {}).get('vector_store', {})
            print(f"✓ Status retrieved!")
            print(f"  - Total vectors: {stats.get('total_vectors', 0)}")
            print(f"  - Metadata count: {stats.get('metadata_count', 0)}")
            return data
        else:
            print(f"✗ Status check failed: {response.text}")
            return None
    except Exception as e:
        print(f"✗ Error checking status: {e}")
        return None


def demo_workflow():
    """Run a complete demo workflow"""
    print("=" * 60)
    print("VoxDocs Backend - Example Workflow")
    print("=" * 60)
    
    # Check health
    if not check_api_health():
        print("\n⚠️  Make sure the API is running:")
        print("   python -m uvicorn app.main:app --reload")
        return
    
    # Check status
    get_upload_status()
    
    # Example workflow (uncomment to use with real files)
    """
    # 1. Upload document
    upload_result = upload_document("sample.pdf")
    if not upload_result:
        print("\n⚠️  Could not upload document. Make sure sample.pdf exists.")
        return
    
    time.sleep(2)  # Wait for processing
    
    # 2. Ask questions
    ask_question("What is the main topic of this document?")
    ask_question("Summarize the key points", include_audio=False)
    
    # 3. Speech to text
    if Path(SAMPLE_AUDIO_PATH).exists():
        transcription = speech_to_text(SAMPLE_AUDIO_PATH)
        if transcription:
            ask_question(transcription['text'])
    
    # 4. Text to speech
    text_to_speech("Here is an example of text to speech conversion.")
    
    # Final status
    time.sleep(1)
    get_upload_status()
    """
    
    print("\n" + "=" * 60)
    print("✅ Example script complete!")
    print("=" * 60)
    print("\n📚 API Documentation: http://localhost:8000/docs")
    print("📝 Check DEVELOPMENT.md for more examples")


if __name__ == "__main__":
    demo_workflow()
