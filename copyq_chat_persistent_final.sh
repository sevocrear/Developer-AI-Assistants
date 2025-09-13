#!/bin/bash

# CopyQ Interactive Chat Script (Truly Persistent Window)
# Captures highlighted text and screenshot, starts interactive chat with context
# Uses a single window that stays open and updates in place

# Configuration
CHAT_HISTORY_DIR="$HOME/.copyq_chat_history"
SCREENSHOT_DIR="$HOME/.copyq_screenshots"
API_KEY="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"
MODEL="openrouter/sonoma-sky-alpha"

# Create directories if they don't exist
mkdir -p "$CHAT_HISTORY_DIR" "$SCREENSHOT_DIR"

# Show processing notification
notify-send -t 2000 "Chat Assistant" "Capturing context..."

# Check if copyq command is available
copyq clipboard >/dev/null 2>&1
if [ $? -ne 0 ]; then
    notify-send -t 5000 "Chat Error" "CopyQ is not running or accessible"
    exit 1
fi

# Try to get selected text first (prioritize selection over clipboard)
SELECTED_TEXT=""

# Try to get X11 selection (highlighted text) using xclip first
SELECTED_TEXT=$(xclip -selection primary -o 2>/dev/null)

# If still empty, try copyq selection as fallback
if [ -z "$SELECTED_TEXT" ]; then
    SELECTED_TEXT=$(copyq selection 2>/dev/null)
fi

# If still empty, try xsel as another fallback
if [ -z "$SELECTED_TEXT" ]; then
    SELECTED_TEXT=$(xsel -p 2>/dev/null)
fi

# If still empty, fall back to clipboard content
if [ -z "$SELECTED_TEXT" ]; then
    SELECTED_TEXT=$(copyq clipboard 2>/dev/null)
fi

# If still empty, show error
if [ -z "$SELECTED_TEXT" ]; then
    notify-send -t 3000 "Chat Error" "No text selected or clipboard empty. Please select some text and try again."
    exit 1
fi

# Generate unique session ID
SESSION_ID=$(date +"%Y%m%d_%H%M%S")
SCREENSHOT_FILE="$SCREENSHOT_DIR/screenshot_$SESSION_ID.png"
CHAT_FILE="$CHAT_HISTORY_DIR/chat_$SESSION_ID.json"

# Take screenshot
notify-send -t 2000 "Chat Assistant" "Taking screenshot..."
import -window root "$SCREENSHOT_FILE" 2>/dev/null || scrot "$SCREENSHOT_FILE" 2>/dev/null || gnome-screenshot -f "$SCREENSHOT_FILE" 2>/dev/null

# Check if screenshot was successful
if [ ! -f "$SCREENSHOT_FILE" ] || [ ! -s "$SCREENSHOT_FILE" ]; then
    notify-send -t 3000 "Chat Warning" "Could not take screenshot, continuing with text only"
    SCREENSHOT_FILE=""
    SCREENSHOT_URL=""
else
    # Upload screenshot to temporary hosting service
    notify-send -t 2000 "Chat Assistant" "Uploading screenshot..."
    
    # Try multiple upload services as fallbacks
    SCREENSHOT_URL=""
    
    # Try 0x0.st first (more reliable)
    SCREENSHOT_URL=$(curl -s -F "file=@$SCREENSHOT_FILE" https://0x0.st 2>/dev/null | tr -d '\n' 2>/dev/null)
    
    # If that fails, try file.io
    if [ -z "$SCREENSHOT_URL" ] || [[ "$SCREENSHOT_URL" == *"error"* ]]; then
        SCREENSHOT_URL=$(curl -s -F "file=@$SCREENSHOT_FILE" https://file.io 2>/dev/null | jq -r '.link' 2>/dev/null)
    fi
    
    # If that fails, try tmpfiles.org
    if [ "$SCREENSHOT_URL" = "null" ] || [ -z "$SCREENSHOT_URL" ] || [[ "$SCREENSHOT_URL" == *"error"* ]]; then
        SCREENSHOT_URL=$(curl -s -F "file=@$SCREENSHOT_FILE" https://tmpfiles.org/api/v1/upload 2>/dev/null | jq -r '.data.url' 2>/dev/null)
    fi
    
    # Validate URL
    if [ "$SCREENSHOT_URL" = "null" ] || [ -z "$SCREENSHOT_URL" ] || [[ "$SCREENSHOT_URL" == *"error"* ]] || [[ ! "$SCREENSHOT_URL" == http* ]]; then
        notify-send -t 3000 "Chat Warning" "Could not upload screenshot, continuing with text only"
        SCREENSHOT_URL=""
    else
        notify-send -t 2000 "Chat Assistant" "Screenshot uploaded successfully: ${SCREENSHOT_URL:0:50}..."
    fi
fi

# Initialize chat history
cat > "$CHAT_FILE" << EOF
{
    "session_id": "$SESSION_ID",
    "timestamp": "$(date -Iseconds)",
    "selected_text": "$(echo "$SELECTED_TEXT" | sed 's/"/\\"/g')",
    "screenshot": "$SCREENSHOT_FILE",
    "screenshot_url": "$SCREENSHOT_URL",
    "messages": []
}
EOF

# Prepare initial context message
CONTEXT_MESSAGE="I have selected the following text: \"$SELECTED_TEXT\"

I also took a screenshot of my current screen (if available).

Please help me understand or discuss this content. You can ask me questions about it, explain it, or help me with any related tasks. I'll be asking you questions about this content."

# Add initial context to chat history
jq --arg text "$SELECTED_TEXT" --arg screenshot "$SCREENSHOT_FILE" --arg screenshot_url "$SCREENSHOT_URL" --arg context "$CONTEXT_MESSAGE" \
   '.messages += [{"role": "user", "content": $context, "timestamp": now}]' "$CHAT_FILE" > "$CHAT_FILE.tmp" && mv "$CHAT_FILE.tmp" "$CHAT_FILE"

# Show ready notification
notify-send -t 3000 "Chat Assistant" "Context captured! Starting chat session..."

# Create a temporary file for chat display
CHAT_DISPLAY_FILE="/tmp/copyq_chat_$SESSION_ID.txt"

# Function to update chat display with formatting
update_chat_display() {
    cat > "$CHAT_DISPLAY_FILE" << EOF
=== CopyQ Chat Assistant ===
Session ID: $SESSION_ID
Selected text: $SELECTED_TEXT
Screenshot: $SCREENSHOT_FILE
Screenshot URL: $SCREENSHOT_URL

Context has been captured. You can now ask questions about the selected text and screenshot.

Available commands:
- Type 'exit', 'quit', or 'bye' to end the session
- Type 'help' for available commands
- Type 'history' to show chat history
- Type 'clear' to clear current conversation

=== Chat History ===
EOF

    # Add all messages to display with formatting
    jq -r '.messages[] | 
        if .role == "user" then
            "**YOU:** \(.content)\n"
        elif .role == "assistant" then
            "**ASSISTANT:** \(.content)\n"
        else
            "**SYSTEM:** \(.content)\n"
        end' "$CHAT_FILE" >> "$CHAT_DISPLAY_FILE" 2>/dev/null
}

# Initialize chat display
update_chat_display

# Function to update HTML display (simplified)
update_html_display() {
    # This function is kept for compatibility but we'll use zenity instead
    return 0
}

# Show ready notification
notify-send -t 3000 "Chat Assistant" "Context captured! Starting chat session..."

# Chat loop using zenity for both display and input
while true; do
    # Get user input first
    USER_INPUT=$(zenity --entry --title="Chat Input" --text="Enter your question or command:" --width=600)
    
    # Check if user cancelled or closed
    if [ $? -ne 0 ] || [ -z "$USER_INPUT" ]; then
        break
    fi
    
    # Check for exit commands
    case "$USER_INPUT" in
        "exit"|"quit"|"bye")
            notify-send -t 3000 "Chat Assistant" "Session ended. History saved to: $CHAT_FILE"
            break
            ;;
        "help")
            zenity --info --title="Help" --text="Available commands:\nexit/quit/bye - End chat session\nhelp - Show this help\nhistory - Show chat history\nclear - Clear current conversation"
            continue
            ;;
        "history")
            HISTORY_TEXT=$(jq -r '.messages[] | "\(.role): \(.content)"' "$CHAT_FILE" 2>/dev/null || echo "No history available")
            zenity --text-info --title="Chat History" --text="$HISTORY_TEXT" --width=600 --height=400
            continue
            ;;
        "clear")
            jq '.messages = []' "$CHAT_FILE" > "$CHAT_FILE.tmp" && mv "$CHAT_FILE.tmp" "$CHAT_FILE"
            zenity --info --title="Chat" --text="Conversation cleared."
            update_chat_display
            update_html_display
            continue
            ;;
    esac
    
    # Add user message to history
    jq --arg content "$USER_INPUT" --arg timestamp "$(date -Iseconds)" \
       '.messages += [{"role": "user", "content": $content, "timestamp": $timestamp}]' "$CHAT_FILE" > "$CHAT_FILE.tmp" && mv "$CHAT_FILE.tmp" "$CHAT_FILE"
    
    # Update displays with user message
    update_chat_display
    update_html_display
    
    # Show processing notification
    notify-send -t 2000 "Chat Assistant" "Getting AI response..."
    
    # Prepare messages for API call with image support
    if [ -n "$SCREENSHOT_URL" ]; then
        # Create messages with image support for the first message (context)
        MESSAGES=$(jq -c --arg screenshot_url "$SCREENSHOT_URL" '
            .messages | 
            map(
                if .role == "user" and (.content | test("I have selected")) then
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": .content
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": $screenshot_url
                                }
                            }
                        ]
                    }
                else
                    .
                end
            )
        ' "$CHAT_FILE")
    else
        # Use regular text messages if no screenshot
        MESSAGES=$(jq -c '.messages' "$CHAT_FILE")
    fi
    
    # Make API call
    RESPONSE=$(curl -s -X POST "https://openrouter.ai/api/v1/chat/completions" \
        -H "Authorization: Bearer $API_KEY" \
        -H "Content-Type: application/json" \
        -d "{
            \"model\": \"$MODEL\",
            \"messages\": $MESSAGES,
            \"stream\": false
        }")
    
    # Extract and display response
    ASSISTANT_RESPONSE=$(echo "$RESPONSE" | jq -r '.choices[0].message.content' 2>/dev/null)
    
    if [ "$ASSISTANT_RESPONSE" = "null" ] || [ -z "$ASSISTANT_RESPONSE" ]; then
        ASSISTANT_RESPONSE="Error: Failed to get response from API"
        zenity --error --title="API Error" --text="Failed to get response from API"
    else
        # Add assistant response to history
        jq --arg content "$ASSISTANT_RESPONSE" --arg timestamp "$(date -Iseconds)" \
           '.messages += [{"role": "assistant", "content": $content, "timestamp": $timestamp}]' "$CHAT_FILE" > "$CHAT_FILE.tmp" && mv "$CHAT_FILE.tmp" "$CHAT_FILE"
    fi
    
    # Update displays with assistant response
    update_chat_display
    
    # Show updated chat history in a single window
    zenity --text-info --title="CopyQ Chat Assistant - Session $SESSION_ID" \
           --filename="$CHAT_DISPLAY_FILE" \
           --width=800 --height=600 \
           --editable=false
done

# Clean up temporary files
rm -f "$CHAT_DISPLAY_FILE"

echo "Chat session ended. History saved to: $CHAT_FILE"
