#!/bin/bash

# Exit on error
set -e

echo "🧹 Cleaning previous builds..."
rm -rf build dist

echo "🔧 Creating virtual environment for build..."
python -m venv .venv-build
source .venv-build/bin/activate

echo "📦 Installing dependencies..."
pip install -r requirements.txt
pip install py2app

echo "📦 Installing project package..."
pip install -e .

echo "🏗️ Building application..."
python setup.py py2app

echo "🧹 Cleaning up build environment..."
deactivate
rm -rf .venv-build

echo "📲 Installing to Applications..."
if [ -d "/Applications/Project Manager.app" ]; then
    echo "  Removing old version..."
    rm -rf "/Applications/Project Manager.app"
fi
echo "  Copying new version..."
cp -r "dist/Project Manager.app" /Applications/

echo "✅ Build and installation complete!"
echo "  The app has been installed to /Applications/Project Manager.app"