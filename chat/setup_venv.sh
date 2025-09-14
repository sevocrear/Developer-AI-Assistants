#!/bin/bash
# Setup script for CopyQ Chat Assistant Python Environment

set -e  # Exit on any error

echo "🚀 Setting up CopyQ Chat Assistant Python Environment..."

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+ first."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✅ Found Python $PYTHON_VERSION"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing Python packages..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p ~/.copyq_screenshots
mkdir -p ~/.copyq_chat_history

# Make scripts executable
echo "🔐 Making scripts executable..."
chmod +x copyq_chat_command.sh
chmod +x copyq_chat.py

# Test installation
echo "🧪 Testing installation..."
python3 -c "
import requests
import PIL
import pyperclip
import pynput
print('✅ All required packages imported successfully!')
"

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Set your OpenRouter API key:"
echo "   export OPENROUTER_API_KEY='your-api-key-here'"
echo ""
echo "2. Add command to CopyQ:"
echo "   Command: $SCRIPT_DIR/copyq_chat_command.sh"
echo "   Shortcut: Ctrl+Shift+I"
echo ""
echo "3. Test the application:"
echo "   source venv/bin/activate"
echo "   python3 copyq_chat.py --help"
echo ""
echo "📖 For detailed instructions, see CopyQ_Chat_Setup.md"
