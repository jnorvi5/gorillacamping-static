#!/usr/bin/env bash

# Upgrade pip
echo "🔧 Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📦 Installing dependencies from requirements.txt..."
pip install -r requirements.txt
