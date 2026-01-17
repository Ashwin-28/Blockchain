#!/bin/bash
set -e

echo "🔧 Preparing to install MongoDB 7.0..."

# Install prerequisites
sudo apt-get update
sudo apt-get install -y gnupg curl

# Import public key
echo "🔑 Importing MongoDB public key..."
curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | \
   sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg \
   --dearmor --yes

# Create list file (Using Jammy repo as Noble is not yet fully published, but compatible with libssl3)
echo "📝 Adding MongoDB repository..."
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | \
   sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

# Update and Install
echo "⬇️  Updating package list and installing..."
sudo apt-get update
sudo apt-get install -y mongodb-org

# Start Service
echo "🚀 Starting MongoDB Service..."
sudo systemctl start mongod
sudo systemctl enable mongod

# Status
echo "✅ MongoDB Status:"
sudo systemctl status mongod --no-pager

echo "🎉 Installation Complete! The backend should now connect automatically."
