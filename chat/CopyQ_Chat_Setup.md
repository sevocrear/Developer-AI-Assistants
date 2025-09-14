# CopyQ Chat Assistant - Python Implementation

A modern, clean Python-based chat assistant for CopyQ integration with screenshot and text analysis capabilities.

## Features

- 🖼️ **Screenshot Capture**: Multiple methods (mss, gnome-screenshot, scrot, ImageMagick)
- 📝 **Text Selection**: Captures highlighted text or clipboard content
- 🌐 **Modern Web Interface**: Beautiful, responsive chat interface with markdown formatting
- 🔗 **Image Upload**: Automatic upload to temporary hosting services (0x0.st, file.io, tmpfiles.org)
- 🤖 **AI Integration**: OpenRouter API with multimodal support for image analysis
- ⚙️ **Configurable**: Command-line arguments and environment variables
- 📚 **Session History**: Persistent chat history storage
- 🚪 **Exit Commands**: Type `bye`, `exit`, `close`, or `quit` to end session
- 🎨 **Markdown Rendering**: Beautiful formatting for headers, bold, italic, code, lists, and links

## Installation

### 1. Setup Virtual Environment (Recommended)

```bash
# Run the automated setup script
./setup_venv.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Install Python Dependencies

```bash
# Activate virtual environment first
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

### 3. Set Environment Variables

```bash
# Required: OpenRouter API Key
export OPENROUTER_API_KEY="your-api-key-here"

# Optional: Model selection
export OPENROUTER_MODEL="openrouter/sonoma-sky-alpha"

# Optional: Browser preference
export COPYQ_CHAT_BROWSER="yandex-browser"

# Optional: Port for web server
export COPYQ_CHAT_PORT="8085"
```

### 4. Install System Dependencies

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3-pip python3-venv python3-tk python3-dev
sudo apt install gnome-screenshot scrot imagemagick xclip xsel copyq

# For better screenshot support
sudo apt install python3-mss
```

## CopyQ Setup

### 1. Add Command to CopyQ

1. **Open CopyQ** and press `F6`

* **Add New Command:**
  - Click the `+Add` button to add a new command
  - Set the following properties:

**Name**: `Chat Assistant`
**Command**: `/path/to/your/copyq_chat_command.sh`
**Global Shortcut**: `Ctrl+Shift+I`
**Icon**: Choose a chat icon

## Usage

### Basic Usage

1. **Select text** or **copy to clipboard**
2. Press **Ctrl+Shift+I**
3. Chat interface opens in browser
4. Ask questions about your content

### Command Line Usage

```bash
# Activate virtual environment first
source venv/bin/activate

# Basic usage
python3 copyq_chat.py

# With custom parameters
python3 copyq_chat.py --api-key "your-key" --model "openrouter/sonoma-sky-alpha" --port 8085

# Help
python3 copyq_chat.py --help
```

### Exit Commands

To end your chat session, simply type any of these commands:

- `bye`
- `exit`
- `close`
- `quit`

The application will gracefully shut down and close the browser window.

### Environment Variables

| Variable               | Default                         | Description             |
| ---------------------- | ------------------------------- | ----------------------- |
| `OPENROUTER_API_KEY` | Required                        | Your OpenRouter API key |
| `OPENROUTER_MODEL`   | `openrouter/sonoma-sky-alpha` | AI model to use         |
| `COPYQ_CHAT_BROWSER` | `yandex-browser`              | Preferred browser       |
| `COPYQ_CHAT_PORT`    | `8085`                        | Web server port         |

## Architecture

### Components

1. **Config**: Configuration management with CLI args
2. **ScreenshotCapture**: Multiple screenshot methods
3. **TextCapture**: Text selection and clipboard handling
4. **ImageUploader**: Upload to temporary hosting services
5. **OpenRouterAPI**: AI API client
6. **ChatHistory**: Session persistence
7. **WebChatServer**: Modern web interface
8. **CopyQChatApp**: Main application orchestrator

### Screenshot Methods

The application tries multiple screenshot methods in order:

1. `mss` (Python library - fastest)
2. `gnome-screenshot` (GNOME)
3. `scrot` (X11)
4. `import` (ImageMagick)

### Image Upload Services

Multiple upload services for reliability:

1. `0x0.st` (Primary - uses curl for best compatibility)
2. `file.io` (Fallback)
3. `tmpfiles.org` (Fallback)

### Markdown Support

The chat interface supports full markdown rendering:

- **Headers**: `#`, `##`, `###`
- **Bold**: `**text**` or `__text__`
- **Italic**: `*text*` or `_text_`
- **Code**: `` `code` `` and ``code blocks``
- **Lists**: `- item` or `* item`
- **Links**: `[text](url)`

## Configuration

### Command Line Arguments

```bash
python3 copyq_chat.py [OPTIONS]

Options:
  --api-key TEXT     OpenRouter API key
  --model TEXT       OpenRouter model to use
  --browser TEXT     Browser to use
  --port INTEGER     Port for web server
  --help             Show help message
```

## Troubleshooting

### Common Issues

1. **"Missing required library"**

   ```bash
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. **"Python3 not found"**

   ```bash
   sudo apt install python3 python3-pip python3-venv
   ```
3. **"Screenshot failed"**

   ```bash
   sudo apt install gnome-screenshot scrot imagemagick xclip xsel
   ```
4. **"API key not set"**

   ```bash
   export OPENROUTER_API_KEY="your-key-here"
   ```
5. **"Port already in use"**

   ```bash
   export COPYQ_CHAT_PORT="8086"
   ```
6. **"Image upload failed"**

   - Check internet connection
   - Try different upload service by modifying the order in `ImageUploader`
7. **"Markdown not rendering"**

   - Clear browser cache
   - Check browser console for JavaScript errors
