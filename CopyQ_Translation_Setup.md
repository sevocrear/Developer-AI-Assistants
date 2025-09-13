# CopyQ Translation Setup Instructions

## Overview

This setup creates a CopyQ command that translates clipboard content between English and Russian using the OpenRouter API, displaying results as disappearing popup notifications.

## Use Cases

This translation tool is perfect for:

- 📖 **Reading Articles**: Quickly translate foreign language articles while browsing
- 📚 **Tech Documentation**: Understand technical documentation in other languages
- 💬 **Chatting with Foreigners**: Translate messages in real-time conversations
- 🌍 **Language Learning**: Get context examples and translations for vocabulary
- 📝 **Content Creation**: Translate text for international audiences
- 🔍 **Research**: Access information from non-English sources

## Prerequisites

- CopyQ installed and running
- `jq` command-line JSON processor installed
- `notify-send` utility (usually comes with desktop environments)
- `xclip` and `xsel` for text selection support
- Internet connection for API calls
- OpenRouter API key

## Installation Steps

### 1. Install Required Dependencies

```bash
# Install jq if not already installed
sudo apt install jq

# Install notify-send if not available
sudo apt install libnotify-bin

# Install xclip and xsel for text selection support
sudo apt install xclip xsel
```

### 2. Setup API Key

Create a `.env` file in the script directory:

```bash
# Create .env file
cat > .env << EOF
OPENROUTER_API_KEY=your-api-key-here
EOF
```

Replace `your-api-key-here` with your actual OpenRouter API key.

### 3. CopyQ Command Setup

1. **Open CopyQ** and go to `File` → `Preferences` → `Commands`
2. **Add New Command:**

   - Click the `+` button to add a new command
   - Set the following properties:

   **Command Name:** `Translate EN↔RU`

   **Command:** `/path/to/your/copyq_translate.sh`

   **Shortcut:** Set a keyboard shortcut (e.g., `Ctrl+Shift+T`)

   **Icon:** Choose a translation icon (optional)

   **Description:** `Translate clipboard content between English and Russian`
3. **Advanced Settings:**

   - **Input:** `text/plain`
   - **Output:** `text/plain`
   - **Automatic:** Check this if you want automatic translation
   - **Show in menu:** Check this to show in context menu

### 3. Alternative: Manual Command Creation

If you prefer to create the command directly in CopyQ:

1. Open CopyQ
2. Go to `File` → `Preferences` → `Commands`
3. Click `+` to add new command
4. Use this configuration:

```json
{
    "name": "Translate EN↔RU",
    "command": "/path/to/your/copyq_translate.sh",
    "shortcut": "Ctrl+Shift+T",
    "description": "Translate clipboard content between English and Russian",
    "input": "text/plain",
    "output": "text/plain",
    "automatic": false,
    "showInMenu": true
}
```

## Usage

### Quick Translation

1. **Select any text** (highlight it with mouse)
2. Press `Ctrl+Shift+T` (or your assigned shortcut)
3. Translation appears as popup notification
4. Translation is also added to CopyQ history
5. **No need to copy text first!**

### Alternative Methods

- **Context Menu**: Right-click CopyQ tray icon → "Translate EN↔RU"
- **CopyQ Window**: Select text item → Right-click → "Translate EN↔RU"

## Features

- **Automatic Language Detection:** Translates English→Russian or Russian→English
- **Context Examples:** Provides usage examples in both languages
- **Popup Notifications:** Shows translation as disappearing notification (8 seconds)
- **Clipboard Integration:** Adds translation to CopyQ history
- **Error Handling:** Shows error notifications for empty clipboard or API failures

## Customization

### Change Notification Duration

Edit the script and modify the `-t` parameter in `notify-send`:

```bash
notify-send -t 8000 "Translation Result" "$CLEAN_TRANSLATION"
```

- `-t 3000` = 3 seconds
- `-t 8000` = 8 seconds (default)
- `-t 15000` = 15 seconds

### Change API Model

Edit the script and modify the model parameter:

```bash
"model": "nvidia/nemotron-nano-9b-v2:free",
```

### Add More Languages

Modify the prompt in the script to support additional languages:

```bash
"content": "Translate to Russian if input is English/other language, translate to English if input is Russian, translate to Spanish if input is German. Word: $CLIPBOARD_TEXT"
```

## Troubleshooting

### Common Issues

1. **"jq: command not found"**
   ```bash
   sudo apt install jq
   ```

2. **"notify-send: command not found"**
   ```bash
   sudo apt install libnotify-bin
   ```

3. **"xclip: command not found" or "xsel: command not found"**
   ```bash
   sudo apt install xclip xsel
   ```

4. **"OPENROUTER_API_KEY not set"**
   - Create `.env` file with your API key
   - Or export: `export OPENROUTER_API_KEY="your-key"`

5. **Permission denied**
   ```bash
   chmod +x /path/to/your/copyq_translate.sh
   ```

6. **"Cannot connect to server! Start CopyQ server first"**
   ```bash
   copyq &
   ```

7. **"Clipboard is empty" when text is selected**
   - Script prioritizes selected text over clipboard
   - No need to copy text first! Just select and press Ctrl+Shift+T
   - Make sure CopyQ server is running: `copyq &`

8. **Shortcut not working**
   - Ensure CopyQ server is running
   - Check "On global shortcut" is enabled in CopyQ Commands
   - Verify script path is correct and executable

9. **API errors**
   - Check internet connection
   - Verify API key is valid in `.env` file
   - Check API quota limits

### Testing the Script

Test the script manually:
```bash
/path/to/your/copyq_translate.sh
```

## Security Notes

- API key is loaded from `.env` file (git-safe)
- Script only sends clipboard text to translation API
- No personal data is stored or logged
- `.env` file is ignored by git (see `.gitignore`)

## API Information

- **Provider:** OpenRouter
- **Model:** nvidia/nemotron-nano-9b-v2:free
- **Endpoint:** https://openrouter.ai/api/v1/chat/completions
- **Rate Limits:** Check OpenRouter documentation for current limits

## Customization

### Change Notification Duration
Edit the script and modify the `-t` parameter:
```bash
notify-send -t 3000 "Translation Result" "$CLEAN_TRANSLATION"
```

### Change API Model
Edit the script and modify the model parameter:
```bash
"model": "nvidia/nemotron-nano-9b-v2:free",
```

### Add More Languages
Modify the prompt in the script:
```bash
"content": "Translate to Russian if input is English/other language, translate to English if input is Russian, translate to Spanish if input is German. Word: $CLIPBOARD_TEXT"
```
