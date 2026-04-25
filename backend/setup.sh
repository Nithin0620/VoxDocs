#!/bin/bash

# VoxDocs Backend - Setup Script
# This script sets up the development environment

set -e  # Exit on error

echo "🚀 VoxDocs Backend Setup"
echo "========================\n"

# Check Python version
echo "✓ Checking Python version..."
python --version

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "✓ Creating virtual environment..."
    python -m venv venv
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "✓ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "✓ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "✓ Installing dependencies..."
pip install -r requirements.txt

# Setup environment file
if [ ! -f ".env" ]; then
    echo "✓ Creating .env file from example..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file with your API keys:"
    echo "   - OPENAI_API_KEY=your_key_here"
    echo "   - ELEVENLABS_API_KEY=your_key_here"
else
    echo "✓ .env file already exists"
fi

# Create necessary directories
echo "✓ Creating directories..."
mkdir -p uploads vectors logs

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Run: source venv/bin/activate"
echo "3. Run: python -m uvicorn app.main:app --reload"
echo ""
echo "API Documentation: http://localhost:8000/docs"
