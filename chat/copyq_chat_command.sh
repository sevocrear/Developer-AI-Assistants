#!/bin/bash
# CopyQ Chat Command - Virtual Environment Wrapper

# Change to the directory where this script is located
cd "$(dirname "$0")"

source ../.env
# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Virtual environment path
VENV_PATH="$SCRIPT_DIR/venv"

# Python script path
PYTHON_SCRIPT="$SCRIPT_DIR/copyq_chat.py"

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    notify-send -t 5000 "CopyQ Chat Error" "Virtual environment not found. Please run: ./setup_venv.sh"
    exit 1
fi

# Check if Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    notify-send -t 5000 "CopyQ Chat Error" "Python script not found: $PYTHON_SCRIPT"
    exit 1
fi

# Show processing notification
notify-send -t 2000 "CopyQ Chat" "Starting chat assistant..."

# Activate virtual environment and run Python application
source "$VENV_PATH/bin/activate" && python3 "$PYTHON_SCRIPT" "$@"