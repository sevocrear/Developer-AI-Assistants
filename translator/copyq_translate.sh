#!/bin/bash

# CopyQ Translation Script
# Translates clipboard content between English and Russian using OpenRouter API
# Shows result as disappearing popup notification
# Change to the directory where this script is located
cd "$(dirname "$0")"

# Load environment variables from .env file
source ../.env

# Check if API key is set
if [ -z "$OPENROUTER_API_KEY" ]; then
    notify-send -t 5000 "Translation Error" "OPENROUTER_API_KEY not set. Please add it to .env file or export it."
    exit 1
fi

# Show processing notification immediately
notify-send -t 2000 "Translation" "Processing translation..."

# Check if copyq command is available
copyq clipboard >/dev/null 2>&1
if [ $? -ne 0 ]; then
    notify-send -t 5000 "Translation Error" "CopyQ is not running or accessible"
    exit 1
fi

# Try to get selected text first (prioritize selection over clipboard)
CLIPBOARD_TEXT=""

# Try to get X11 selection (highlighted text) using xclip first
CLIPBOARD_TEXT=$(xclip -selection primary -o 2>/dev/null)

# If still empty, try copyq selection as fallback
if [ -z "$CLIPBOARD_TEXT" ]; then
    CLIPBOARD_TEXT=$(copyq selection 2>/dev/null)
fi

# If still empty, try xsel as another fallback
if [ -z "$CLIPBOARD_TEXT" ]; then
    CLIPBOARD_TEXT=$(xsel -p 2>/dev/null)
fi

# If still empty, fall back to clipboard content
if [ -z "$CLIPBOARD_TEXT" ]; then
    CLIPBOARD_TEXT=$(copyq clipboard 2>/dev/null)
fi

# If still empty, show error
if [ -z "$CLIPBOARD_TEXT" ]; then
    notify-send -t 3000 "Translation Error" "No text selected or clipboard empty. Please select some text and try again."
    exit 1
fi

# Show that we're making API call
notify-send -t 2000 "Translation" "Calling translation API..."

# Prepare the JSON payload
JSON_PAYLOAD=$(cat <<EOF
{
    "model": "nvidia/nemotron-nano-9b-v2:free",
    "messages": [
        {
            "role": "user",
            "content": "Translate, please, in to russian if word is in english or any other language. If its in russian, translate to english. Also, provide some context examples. Word: $CLIPBOARD_TEXT"
        }
    ]
}
EOF
)

# Make API call
RESPONSE=$(curl -s -X POST "https://openrouter.ai/api/v1/chat/completions" \
    -H "Authorization: Bearer $OPENROUTER_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$JSON_PAYLOAD")

# Extract translation from response
TRANSLATION=$(echo "$RESPONSE" | jq -r '.choices[0].message.content' 2>/dev/null)

# Check if translation was successful
if [ "$TRANSLATION" = "null" ] || [ -z "$TRANSLATION" ]; then
    notify-send -t 5000 "Translation Error" "Failed to get translation from API"
    exit 1
fi

# Clean up the translation text (remove markdown formatting for notification)
CLEAN_TRANSLATION=$(echo "$TRANSLATION" | sed 's/\*\*//g' | sed 's/\*//g' | sed 's/---//g')

# Extract just the main translation (first few lines before examples)
MAIN_TRANSLATION=$(echo "$CLEAN_TRANSLATION" | head -n 3 | tr '\n' ' ' | sed 's/  */ /g')

# Show notification with main translation (concise)
notify-send -t 8000 "Translation" "$MAIN_TRANSLATION"

# For full translation, use zenity to show in a dialog box
FULL_TRANSLATION=$(echo "$CLEAN_TRANSLATION" | head -n 20)
zenity --info --title="Full Translation:" --text="$FULL_TRANSLATION" --width=600 --height=400 &

# Also copy the translation to clipboard
echo "$TRANSLATION" | copyq add -
