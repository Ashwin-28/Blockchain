#!/bin/bash

# ================================================
# Decentralized Biometric Identity System
# Setup Script
# ================================================

set -e

echo "================================================"
echo "  Biometric Identity System Setup"
echo "================================================"
echo ""

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+"
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'.' -f1 | tr -d 'v')
if [ "$NODE_VERSION" -lt 16 ]; then
    echo "❌ Node.js version 16+ required. Current: $(node -v)"
    exit 1
fi
echo "✓ Node.js $(node -v)"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi
echo "✓ Python $(python3 --version)"

# Install root dependencies
echo ""
echo "Installing root dependencies..."
npm install

# Install frontend dependencies
echo ""
echo "Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Setup backend
echo ""
echo "Setting up backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate

cd ..

# Create directories
mkdir -p backend/uploads
mkdir -p backend/storage

# Copy env file if not exists
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ Created .env file from template"
fi

echo ""
echo "================================================"
echo "  Setup Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo "  1. Configure .env with your settings"
echo "  2. Start Ganache: npm run ganache"
echo "  3. Deploy contracts: npm run migrate"
echo "  4. Start backend: npm run backend"
echo "  5. Start frontend: npm run frontend"
echo ""
