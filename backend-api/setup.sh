#!/bin/bash

# MedXP Backend Setup Script

echo "🏥 Setting up MedXP Backend API..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python found: $(python3 --version)"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check for .env file
if [ ! -f .env ]; then
    echo "📝 Creating .env file from example..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Please edit backend-api/.env and add your Minimax API credentials"
    echo "   MINIMAX_API_KEY and MINIMAX_GROUP_ID"
    echo "   Get your credentials from: https://www.minimaxi.com/"
    echo ""
fi

echo ""
echo "✅ Backend setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit backend-api/.env and add your Minimax API credentials"
echo "  2. Run: cd backend-api && source venv/bin/activate"
echo "  3. Run: python main.py"
echo ""
