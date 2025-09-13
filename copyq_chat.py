#!/usr/bin/env python3
"""
CopyQ Chat Assistant - Modern Python Implementation
A clean, efficient chat interface for CopyQ integration with screenshot and text analysis.

Features:
- Screenshot capture with multiple methods
- Text selection and clipboard handling
- Modern web interface
- Image upload to temporary hosting
- OpenRouter API integration
- Session history management
- Command-line configuration
"""

import argparse
import json
import os
import sys
import tempfile
import time
import webbrowser
import subprocess
import threading
import http.server
import socketserver
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from urllib.parse import urlparse

# Third-party imports with fallbacks
try:
    import requests
    from PIL import Image
    import pyperclip
    import mss
    from flask import Flask, request, jsonify, render_template_string
    from dotenv import load_dotenv
except ImportError as e:
    print(f"❌ Missing required library: {e}")
    print("📦 Please run: ./setup_venv.sh")
    sys.exit(1)


@dataclass
class Config:
    """Configuration management with environment variables and CLI args."""
    api_key: str
    model: str = "openrouter/sonoma-sky-alpha"
    browser: str = "yandex-browser"
    port: int = 8085
    screenshot_dir: Path = Path.home() / '.copyq_screenshots'
    chat_history_dir: Path = Path.home() / '.copyq_chat_history'
    
    def __post_init__(self):
        """Initialize after dataclass creation."""
        self.screenshot_dir.mkdir(exist_ok=True)
        self.chat_history_dir.mkdir(exist_ok=True)
    
    @classmethod
    def from_args(cls, args: argparse.Namespace) -> 'Config':
        """Create config from command line arguments."""
        # Load environment variables
        load_dotenv()
        
        # Get API key from args or environment
        api_key = args.api_key or os.getenv('OPENROUTER_API_KEY', '')
        if not api_key:
            print("❌ Error: OPENROUTER_API_KEY not provided")
            print("💡 Set it via: export OPENROUTER_API_KEY='your-key'")
            print("💡 Or pass: --api-key 'your-key'")
            sys.exit(1)
        
        return cls(
            api_key=api_key,
            model=args.model or os.getenv('OPENROUTER_MODEL', 'openrouter/sonoma-sky-alpha'),
            browser=args.browser or os.getenv('COPYQ_CHAT_BROWSER', 'yandex-browser'),
            port=args.port or int(os.getenv('COPYQ_CHAT_PORT', '8085'))
        )


class ScreenshotCapture:
    """Modern screenshot capture with multiple fallback methods."""
    
    @staticmethod
    def capture_screenshot() -> Optional[str]:
        """Capture screenshot using the best available method."""
        timestamp = int(time.time())
        filename = f"screenshot_{timestamp}.png"
        filepath = Config.screenshot_dir / filename
        
        # Try different screenshot methods in order of preference
        methods = [
            ScreenshotCapture._capture_with_mss,
            ScreenshotCapture._capture_with_gnome_screenshot,
            ScreenshotCapture._capture_with_scrot,
            ScreenshotCapture._capture_with_import,
        ]
        
        for method in methods:
            try:
                if method(filepath):
                    print(f"📸 Screenshot captured: {filepath}")
                    return str(filepath)
            except Exception as e:
                print(f"⚠️ Screenshot method failed: {e}")
                continue
        
        print("❌ All screenshot methods failed")
        return None
    
    @staticmethod
    def _capture_with_mss(filepath: Path) -> bool:
        """Capture using mss (fastest method)."""
        try:
            with mss.mss() as sct:
                # Capture the entire screen
                monitor = sct.monitors[1]  # Primary monitor
                screenshot = sct.grab(monitor)
                
                # Convert to PIL Image and save
                img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                img.save(filepath)
                return filepath.exists()
        except Exception:
            return False
    
    @staticmethod
    def _capture_with_gnome_screenshot(filepath: Path) -> bool:
        """Capture using gnome-screenshot."""
        try:
            result = subprocess.run([
                'gnome-screenshot', '-f', str(filepath)
            ], capture_output=True, timeout=5)
            return result.returncode == 0 and filepath.exists()
        except:
            return False
    
    @staticmethod
    def _capture_with_scrot(filepath: Path) -> bool:
        """Capture using scrot."""
        try:
            result = subprocess.run([
                'scrot', str(filepath)
            ], capture_output=True, timeout=5)
            return result.returncode == 0 and filepath.exists()
        except:
            return False
    
    @staticmethod
    def _capture_with_import(filepath: Path) -> bool:
        """Capture using ImageMagick import."""
        try:
            result = subprocess.run([
                'import', '-window', 'root', str(filepath)
            ], capture_output=True, timeout=5)
            return result.returncode == 0 and filepath.exists()
        except:
            return False


class TextCapture:
    """Text capture from selection and clipboard."""
    
    @staticmethod
    def get_selected_text() -> Optional[str]:
        """Get currently selected text (primary selection)."""
        try:
            # Try xclip first (primary selection)
            result = subprocess.run([
                'xclip', '-selection', 'primary', '-o'
            ], capture_output=True, text=True, timeout=2)
            
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except:
            pass
        
        try:
            # Try xsel as fallback
            result = subprocess.run([
                'xsel', '-p'
            ], capture_output=True, text=True, timeout=2)
            
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except:
            pass
        
        return None
    
    @staticmethod
    def get_clipboard_text() -> Optional[str]:
        """Get clipboard text."""
        try:
            return pyperclip.paste()
        except:
            return None
    
    @staticmethod
    def get_text_context() -> str:
        """Get text context (selected text or clipboard)."""
        selected = TextCapture.get_selected_text()
        if selected:
            return selected
        
        clipboard = TextCapture.get_clipboard_text()
        return clipboard or ""


class ImageUploader:
    """Upload images to temporary hosting services."""
    
    @staticmethod
    def upload_image(filepath: str) -> Optional[str]:
        """Upload image and return public URL."""
        services = [
            ImageUploader._upload_to_0x0,
            ImageUploader._upload_to_fileio,
            ImageUploader._upload_to_tmpfiles
        ]
        
        for service in services:
            try:
                url = service(filepath)
                if url:
                    print(f"📤 Image uploaded: {url[:50]}...")
                    return url
            except Exception as e:
                print(f"⚠️ Upload service failed: {e}")
                continue
        
        print("❌ All upload services failed")
        return None
    
    @staticmethod
    def _upload_to_0x0(filepath: str) -> Optional[str]:
        """Upload to 0x0.st (most reliable)."""
        try:
            import subprocess
            result = subprocess.run([
                'curl', '-s', '-F', f'file=@{filepath}', 'https://0x0.st'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                url = result.stdout.strip()
                # Check if URL is valid (not an error message)
                if url and url.startswith('https://') and not any(word in url.lower() for word in ['error', 'failed', 'invalid']):
                    return url
        except Exception as e:
            print(f"⚠️ 0x0.st upload failed: {e}")
        return None
    
    @staticmethod
    def _upload_to_fileio(filepath: str) -> Optional[str]:
        """Upload to file.io."""
        try:
            with open(filepath, 'rb') as f:
                response = requests.post('https://file.io', files={'file': f}, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    link = data.get('link')
                    if link and link != 'null':
                        return link
        except Exception as e:
            print(f"⚠️ file.io upload failed: {e}")
        return None
    
    @staticmethod
    def _upload_to_tmpfiles(filepath: str) -> Optional[str]:
        """Upload to tmpfiles.org."""
        try:
            with open(filepath, 'rb') as f:
                response = requests.post('https://tmpfiles.org/api/v1/upload', files={'file': f}, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    url = data.get('data', {}).get('url')
                    if url and url != 'null':
                        # Convert http to https for better compatibility
                        if url.startswith('http://'):
                            url = url.replace('http://', 'https://', 1)
                        return url
        except Exception as e:
            print(f"⚠️ tmpfiles.org upload failed: {e}")
        return None


class OpenRouterAPI:
    """OpenRouter API client."""
    
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
    
    def chat_completion(self, messages: List[Dict[str, Any]], image_url: Optional[str] = None) -> Optional[str]:
        """Send chat completion request."""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # Check if model supports multimodal (images)
            multimodal_models = [
                'anthropic/claude-3.5-sonnet',
                'anthropic/claude-3.5-haiku',
                'anthropic/claude-3-haiku',
                'anthropic/claude-3-opus',
                'openai/gpt-4o',
                'openai/gpt-4o-mini',
                'openai/chatgpt-4o-latest',
                'meta-llama/llama-3.2-90b-vision-instruct',
                'meta-llama/llama-3.2-11b-vision-instruct',
                'x-ai/grok-2-vision-1212',
                'openrouter/sonoma-sky-alpha'
            ]
            
            # Prepare messages with image if available and model supports it
            if image_url and messages and self.model in multimodal_models:
                first_message = messages[0]
                if isinstance(first_message.get('content'), str):
                    first_message['content'] = [
                        {'type': 'text', 'text': first_message['content']},
                        {'type': 'image_url', 'image_url': {'url': image_url}}
                    ]
                print(f"🖼️ Using multimodal mode with image: {image_url[:50]}...")
            elif image_url:
                # Add image URL as text description for non-multimodal models
                first_message = messages[0]
                if isinstance(first_message.get('content'), str):
                    first_message['content'] += f"\n\n[Screenshot available at: {image_url}]"
                print(f"📝 Adding image URL as text description (model doesn't support multimodal)")
            
            data = {
                'model': self.model,
                'messages': messages,
                'stream': False
            }
            
            print(f"🤖 Sending request to {self.model}...")
            
            response = requests.post(self.base_url, headers=headers, json=data, timeout=30)
            
            if response.status_code != 200:
                print(f"❌ API error {response.status_code}: {response.text}")
                return None
                
            response.raise_for_status()
            
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content']
            
        except Exception as e:
            print(f"❌ API request failed: {e}")
        
        return None


class ChatHistory:
    """Chat history management."""
    
    def __init__(self, history_dir: Path):
        self.history_dir = history_dir
    
    def save_session(self, session_id: str, data: Dict[str, Any]):
        """Save chat session data."""
        filepath = self.history_dir / f"session_{session_id}.json"
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load chat session data."""
        filepath = self.history_dir / f"session_{session_id}.json"
        if filepath.exists():
            with open(filepath, 'r') as f:
                return json.load(f)
        return None


class WebChatServer:
    """Modern web-based chat interface using Flask."""
    
    def __init__(self, config: Config):
        self.config = config
        self.api = OpenRouterAPI(config.api_key, config.model)
        self.history = ChatHistory(config.chat_history_dir)
        self.session_id = str(int(time.time()))
        self.context_data = {}
        self.app = Flask(__name__)
        self.setup_routes()
    
    def setup_routes(self):
        """Setup Flask routes."""
        
        @self.app.route('/')
        def index():
            return self.generate_chat_html()
        
        @self.app.route('/api/chat', methods=['POST'])
        def chat():
            try:
                data = request.get_json()
                messages = data.get('messages', [])
                
                # Check for exit commands
                if messages:
                    last_message = messages[-1].get('content', '').lower().strip()
                    if last_message in ['bye', 'exit', 'close', 'quit']:
                        # Schedule server shutdown
                        def shutdown_server():
                            time.sleep(1)  # Give time for response
                            # Try graceful shutdown first
                            try:
                                import signal
                                os.kill(os.getpid(), signal.SIGTERM)
                            except:
                                # Fallback to force exit
                                os._exit(0)
                        
                        threading.Thread(target=shutdown_server, daemon=True).start()
                        return jsonify({'success': True, 'response': '👋 Goodbye! Chat session ended.', 'exit': True})
                
                response = self.api.chat_completion(messages, self.context_data.get('image_url'))
                
                if response:
                    return jsonify({'success': True, 'response': response})
                else:
                    return jsonify({'success': False, 'error': 'No response from API'})
                    
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)})
        
        @self.app.route('/api/context', methods=['POST'])
        def context():
            try:
                data = request.get_json()
                self.context_data.update(data)
                
                # Save session
                session_data = {
                    'timestamp': time.time(),
                    'context': self.context_data,
                    'messages': []
                }
                self.history.save_session(self.session_id, session_data)
                
                return jsonify({'success': True})
                
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)})
    
    def generate_chat_html(self) -> str:
        """Generate modern chat interface HTML."""
        selected_text = self.context_data.get('selected_text', '')
        screenshot_url = self.context_data.get('image_url', '')
        
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CopyQ Chat Assistant</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}
        
        .header {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 1rem;
            color: white;
            text-align: center;
        }}
        
        .context-box {{
            background: rgba(255, 255, 255, 0.9);
            margin: 1rem;
            padding: 1rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        .context-item {{
            margin: 0.5rem 0;
        }}
        
        .context-label {{
            font-weight: bold;
            color: #333;
        }}
        
        .chat-container {{
            flex: 1;
            display: flex;
            flex-direction: column;
            margin: 1rem;
            background: rgba(255, 255, 255, 0.9);
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        .chat-messages {{
            flex: 1;
            padding: 1rem;
            overflow-y: auto;
            max-height: 400px;
        }}
        
        .message {{
            margin: 0.5rem 0;
            padding: 0.75rem;
            border-radius: 10px;
            max-width: 80%;
        }}
        
        .message.user {{
            background: #667eea;
            color: white;
            margin-left: auto;
            text-align: right;
        }}
        
        .message.assistant {{
            background: #f0f0f0;
            color: #333;
            margin-right: auto;
        }}
        
        .input-container {{
            display: flex;
            padding: 1rem;
            background: white;
            border-top: 1px solid #eee;
        }}
        
        .input-field {{
            flex: 1;
            padding: 0.75rem;
            border: 1px solid #ddd;
            border-radius: 5px;
            margin-right: 0.5rem;
        }}
        
        .send-button {{
            padding: 0.75rem 1.5rem;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }}
        
        .send-button:hover {{
            background: #5a6fd8;
        }}
        
        .loading {{
            display: none;
            text-align: center;
            padding: 1rem;
            color: #666;
        }}
        
        /* Markdown styling */
        .message h1, .message h2, .message h3 {{
            margin: 0.5rem 0;
            color: #333;
        }}
        
        .message h1 {{
            font-size: 1.5rem;
            border-bottom: 2px solid #667eea;
            padding-bottom: 0.25rem;
        }}
        
        .message h2 {{
            font-size: 1.3rem;
            border-bottom: 1px solid #ddd;
            padding-bottom: 0.25rem;
        }}
        
        .message h3 {{
            font-size: 1.1rem;
            color: #667eea;
        }}
        
        .message code {{
            background: #f4f4f4;
            padding: 0.2rem 0.4rem;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }}
        
        .message pre {{
            background: #f4f4f4;
            padding: 1rem;
            border-radius: 5px;
            overflow-x: auto;
            margin: 0.5rem 0;
        }}
        
        .message pre code {{
            background: none;
            padding: 0;
        }}
        
        .message ul, .message ol {{
            margin: 0.5rem 0;
            padding-left: 1.5rem;
        }}
        
        .message li {{
            margin: 0.25rem 0;
        }}
        
        .message a {{
            color: #667eea;
            text-decoration: none;
        }}
        
        .message a:hover {{
            text-decoration: underline;
        }}
        
        .message strong {{
            font-weight: bold;
        }}
        
        .message em {{
            font-style: italic;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>CopyQ Chat Assistant</h1>
        <p>Session: {self.session_id} | Context: Captured</p>
    </div>
    
    <div class="context-box">
        <div class="context-item">
            <span class="context-label">Selected Text:</span> {selected_text or 'None'}
        </div>
        <div class="context-item">
            <span class="context-label">Screenshot:</span> {screenshot_url or 'None'}
        </div>
        <div class="context-item">
            <span class="context-label">Available Commands:</span> <strong>bye</strong>, <strong>exit</strong>, <strong>close</strong>, <strong>quit</strong> (to end session)
        </div>
    </div>
    
    <div class="chat-container">
        <div class="chat-messages" id="chatMessages">
            <!-- Initial message will be added by JavaScript -->
        </div>
        
        <div class="loading" id="loading">
            Processing your message...
        </div>
        
        <div class="input-container">
            <input type="text" class="input-field" id="messageInput" placeholder="Type your message here...">
            <button class="send-button" onclick="sendMessage()">Send</button>
        </div>
    </div>
    
    <script>
        const selectedText = `{selected_text}`;
        const screenshotUrl = `{screenshot_url}`;
        
        function addMessage(role, content) {{
            const messagesDiv = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${{role}}`;
            
            if (role === 'user') {{
                // User messages: bold formatting
                messageDiv.innerHTML = `<strong>${{content}}</strong>`;
            }} else {{
                // Assistant messages: render markdown
                messageDiv.innerHTML = renderMarkdown(content);
            }}
            
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }}
        
        function renderMarkdown(text) {{
            // Split into lines for better processing
            let lines = text.split('\\n');
            let result = [];
            let inList = false;
            
            for (let i = 0; i < lines.length; i++) {{
                let line = lines[i];
                
                // Headers
                if (line.match(/^### (.*)$/)) {{
                    if (inList) {{ result.push('</ul>'); inList = false; }}
                    result.push('<h3>' + line.replace(/^### (.*)$/, '$1') + '</h3>');
                }} else if (line.match(/^## (.*)$/)) {{
                    if (inList) {{ result.push('</ul>'); inList = false; }}
                    result.push('<h2>' + line.replace(/^## (.*)$/, '$1') + '</h2>');
                }} else if (line.match(/^# (.*)$/)) {{
                    if (inList) {{ result.push('</ul>'); inList = false; }}
                    result.push('<h1>' + line.replace(/^# (.*)$/, '$1') + '</h1>');
                }}
                // Lists
                else if (line.match(/^[-*] (.*)$/)) {{
                    if (!inList) {{ result.push('<ul>'); inList = true; }}
                    let content = line.replace(/^[-*] (.*)$/, '$1');
                    result.push('<li>' + processInlineMarkdown(content) + '</li>');
                }}
                // Empty lines
                else if (line.trim() === '') {{
                    if (inList) {{ result.push('</ul>'); inList = false; }}
                    result.push('<br>');
                }}
                // Regular text
                else {{
                    if (inList) {{ result.push('</ul>'); inList = false; }}
                    result.push(processInlineMarkdown(line));
                }}
            }}
            
            // Close any open list
            if (inList) {{ result.push('</ul>'); }}
            
            return result.join('\\n');
        }}
        
        function processInlineMarkdown(text) {{
            return text
                // Bold
                .replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>')
                .replace(/__(.*?)__/g, '<strong>$1</strong>')
                // Italic
                .replace(/\\*(.*?)\\*/g, '<em>$1</em>')
                .replace(/_(.*?)_/g, '<em>$1</em>')
                // Code blocks
                .replace(/```([\\s\\S]*?)```/g, '<pre><code>$1</code></pre>')
                // Inline code
                .replace(/`(.*?)`/g, '<code>$1</code>')
                // Links
                .replace(/\\[([^\\]]+)\\]\\(([^)]+)\\)/g, '<a href="$2" target="_blank">$1</a>');
        }}
        
        function showLoading() {{
            document.getElementById('loading').style.display = 'block';
        }}
        
        function hideLoading() {{
            document.getElementById('loading').style.display = 'none';
        }}
        
        function sendMessage() {{
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Add user message
            addMessage('user', message);
            input.value = '';
            
            // Show loading
            showLoading();
            
            // Prepare messages for API
            const messages = [
                {{
                    role: 'user',
                    content: `I have selected the following text: "${{selectedText}}"
                    
I also took a screenshot of my current screen (if available).

Please help me understand or discuss this content. You can ask me questions about it, explain it, or help me with any related tasks. I will be asking you questions about this content.`
                }},
                {{
                    role: 'user',
                    content: message
                }}
            ];
            
            // Send to API
            fetch('/api/chat', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json'
                }},
                body: JSON.stringify({{ messages: messages }})
            }})
            .then(response => response.json())
            .then(data => {{
                hideLoading();
                if (data.success) {{
                    addMessage('assistant', data.response);
                    
                    // Check if this is an exit command
                    if (data.exit) {{
                        // Close browser window after a short delay
                        setTimeout(() => {{
                            window.close();
                        }}, 2000);
                    }}
                }} else {{
                    addMessage('assistant', 'Error: ' + data.error);
                }}
            }})
            .catch(error => {{
                hideLoading();
                addMessage('assistant', 'Error: ' + error.message);
            }});
        }}
        
        // Allow Enter key to send message
        document.getElementById('messageInput').addEventListener('keypress', function(e) {{
            if (e.key === 'Enter') {{
                sendMessage();
            }}
        }});
        
        // Initialize welcome message
        document.addEventListener('DOMContentLoaded', function() {{
            const welcomeMessage = `# Welcome to CopyQ Chat Assistant! 🚀
            
I can see your **selected text** and **screenshot**. How can I help you with this content?

## Available Features:
- **Text Analysis**: Ask questions about selected text
- **Image Analysis**: Describe or analyze screenshots  
- **Code Help**: Get explanations and examples
- **Markdown Formatting**: Responses are beautifully formatted

Just type your question and I'll respond with properly formatted markdown!`;
            
            addMessage('assistant', welcomeMessage);
        }});
    </script>
</body>
</html>
        """
    
    def run(self):
        """Run the Flask server."""
        print(f"🌐 Starting chat server on http://localhost:{self.config.port}")
        
        # Set up signal handler for graceful shutdown
        import signal
        def signal_handler(signum, frame):
            print("\n👋 Received shutdown signal. Ending chat session...")
            sys.exit(0)
        
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        
        try:
            self.app.run(host='localhost', port=self.config.port, debug=False)
        except KeyboardInterrupt:
            print("\n👋 Chat session ended by user.")
        except Exception as e:
            print(f"❌ Server error: {e}")


class CopyQChatApp:
    """Main application class."""
    
    def __init__(self, config: Config):
        self.config = config
        self.session_id = str(int(time.time()))
    
    def capture_context(self) -> Dict[str, Any]:
        """Capture screenshot and text context."""
        print("📸 Capturing screenshot...")
        screenshot_path = ScreenshotCapture.capture_screenshot()
        
        print("📝 Capturing text context...")
        selected_text = TextCapture.get_text_context()
        
        image_url = None
        if screenshot_path:
            print("📤 Uploading screenshot...")
            image_url = ImageUploader.upload_image(screenshot_path)
        
        return {
            'selected_text': selected_text,
            'image_url': image_url,
            'screenshot_path': screenshot_path,
            'timestamp': time.time()
        }
    
    def run(self):
        """Run the chat application."""
        print("🚀 CopyQ Chat Assistant - Starting...")
        
        # Capture context
        context_data = self.capture_context()
        
        print(f"📋 Context captured:")
        print(f"  📝 Text: {context_data['selected_text'][:50]}..." if context_data['selected_text'] else "  📝 No text")
        print(f"  📸 Screenshot: {'Yes' if context_data['screenshot_path'] else 'No'}")
        print(f"  🔗 Image URL: {'Yes' if context_data['image_url'] else 'No'}")
        
        # Start web server
        server = WebChatServer(self.config)
        server.context_data = context_data
        
        # Open browser
        url = f"http://localhost:{self.config.port}"
        print(f"🌐 Opening browser: {url}")
        
        try:
            webbrowser.open(url)
        except Exception as e:
            print(f"⚠️ Failed to open browser: {e}")
            print(f"💡 Please manually open: {url}")
        
        # Start server
        try:
            server.run()
        except KeyboardInterrupt:
            print("\n👋 Chat session ended.")
        except Exception as e:
            print(f"❌ Server error: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='CopyQ Chat Assistant - Modern Python Implementation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 copyq_chat.py
  python3 copyq_chat.py --api-key "your-key" --model "openrouter/sonoma-sky-alpha"
  python3 copyq_chat.py --port 8086 --browser "firefox"

Environment Variables:
  OPENROUTER_API_KEY    OpenRouter API key (required)
  OPENROUTER_MODEL      Model to use (default: openrouter/sonoma-sky-alpha)
  COPYQ_CHAT_BROWSER    Browser to use (default: yandex-browser)
  COPYQ_CHAT_PORT       Port for web server (default: 8085)
        """
    )
    
    parser.add_argument('--api-key', help='OpenRouter API key')
    parser.add_argument('--model', help='OpenRouter model to use')
    parser.add_argument('--browser', help='Browser to use')
    parser.add_argument('--port', type=int, help='Port for web server')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Create configuration
    config = Config.from_args(args)
    
    if args.verbose:
        print(f"🔧 Configuration:")
        print(f"  🤖 Model: {config.model}")
        print(f"  🌐 Browser: {config.browser}")
        print(f"  🔌 Port: {config.port}")
        print(f"  📁 Screenshot dir: {config.screenshot_dir}")
        print(f"  📚 History dir: {config.chat_history_dir}")
    
    # Run application
    app = CopyQChatApp(config)
    app.run()


if __name__ == '__main__':
    main()