# CopyQ Translation Setup Instructions

## Overview

This setup creates a CopyQ command that translates clipboard content between English and Russian using the OpenRouter API, displaying results as disappearing popup notifications.

## Prerequisites

- CopyQ installed and running
- `jq` command-line JSON processor installed
- `notify-send` utility (usually comes with desktop environments)
- Internet connection for API calls

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

### 2. CopyQ Command Setup

1. **Open CopyQ** and go to `File` → `Preferences` → `Commands`
2. **Add New Command:**

   - Click the `+` button to add a new command
   - Set the following properties:

   **Command Name:** `Translate EN↔RU`

   **Command:** `/media/sevocrear/data/Crypto_Dir/ATOM/researches/copyq_translate.sh`

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
    "command": "/media/sevocrear/data/Crypto_Dir/ATOM/researches/copyq_translate.sh",
    "shortcut": "Ctrl+Shift+T",
    "description": "Translate clipboard content between English and Russian",
    "input": "text/plain",
    "output": "text/plain",
    "automatic": false,
    "showInMenu": true
}
```

## Usage

### Method 1: Keyboard Shortcut (Recommended)

1. **Select any text** (highlight it with mouse)
2. Press `Ctrl+Shift+T` (or your assigned shortcut)
3. Translation appears as popup notification
4. Translation is also added to CopyQ history
5. **No need to copy text first!**

### Method 2: Context Menu

1. Copy any text to clipboard
2. Right-click CopyQ tray icon
3. Select "Translate EN↔RU" from menu

### Method 3: CopyQ Main Window

1. Open CopyQ main window
2. Select any text item
3. Right-click and choose "Translate EN↔RU"

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

4. **Permission denied**

   ```bash
   chmod +x /media/sevocrear/data/Crypto_Dir/ATOM/researches/copyq_translate.sh
   ```

5. **"Cannot connect to server! Start CopyQ server first"**

   ```bash
   # Start CopyQ server
   copyq &
   ```

6. **"Clipboard is empty" when text is selected**
   - The script now **prioritizes selected text over clipboard content**
   - **No need to copy text first!** Just select text and press Ctrl+Shift+T
   - The script tries: xclip → copyq selection → xsel → clipboard (fallback)
   - **Selected text always takes priority over clipboard**
   - Make sure CopyQ server is running: `copyq &`

7. **Shortcut not working**
   - Make sure CopyQ server is running
   - Check that "On global shortcut" checkbox is checked in CopyQ Commands
   - Verify the script path is correct and executable
   - Try running the script manually first

8. **API errors**

   - Check internet connection
   - Verify API key is valid
   - Check if API quota is exceeded

### Testing the Script

Test the script manually:

```bash
/media/sevocrear/data/Crypto_Dir/ATOM/researches/copyq_translate.sh
```

## Security Notes

- The API key is embedded in the script for convenience
- For production use, consider using environment variables
- The script only sends clipboard text to the translation API
- No personal data is stored or logged

## API Information

- **Provider:** OpenRouter
- **Model:** nvidia/nemotron-nano-9b-v2:free
- **Endpoint:** https://openrouter.ai/api/v1/chat/completions
- **Rate Limits:** Check OpenRouter documentation for current limits

## Script Versions

### Version 1: `copyq_translate.sh` (Full Dialog)

- Shows concise translation in popup notification (8 seconds)
- Opens full translation in zenity dialog box (600x400 pixels)
- Stores full translation in CopyQ history
- **Best for:** Users who want to see full context immediately

### Version 2: `copyq_translate_simple.sh` (Simple Popup)

- Shows only main translation in popup notification (6 seconds)
- Stores full translation in CopyQ history
- Shows confirmation that full translation is saved
- **Best for:** Users who prefer minimal popups and check CopyQ for details

### Choosing Your Version

**Use `copyq_translate.sh` if:**

- You want to see the full translation with examples immediately
- You don't mind a dialog box appearing
- You want comprehensive context

**Use `copyq_translate_simple.sh` if:**

- You prefer clean, minimal popup notifications
- You're okay with checking CopyQ history for full details
- You want faster, less intrusive notifications

### Switching Between Versions

To switch versions, simply change the command path in CopyQ:

- **Full version:** `/media/sevocrear/data/Crypto_Dir/ATOM/researches/copyq_translate.sh`
- **Simple version:** `/media/sevocrear/data/Crypto_Dir/ATOM/researches/copyq_translate_simple.sh`
