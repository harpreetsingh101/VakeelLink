import os
import sys
import time
import threading
import urllib.request
import webbrowser
from pathlib import Path

# Ensure HuggingFace runs offline with cached model
os.environ["HF_HUB_OFFLINE"] = "1"

# Resolve backend directory
ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "Vakeel-link-main" / "backend"
sys.path.insert(0, str(BACKEND_DIR))
os.chdir(BACKEND_DIR)

def wait_and_open_browser():
    """Wait until the FastAPI server is actually responding before opening browser."""
    print("[VakeelLink] Loading AI models & server components (takes ~5-8 seconds)...")
    for attempt in range(40):
        time.sleep(1)
        try:
            with urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=1) as resp:
                if resp.status == 200:
                    print("\n" + "="*65)
                    print("  >>> SUCCESS! VakeelLink is live and ready:")
                    print("  >>> [1] Home Page:          http://127.0.0.1:8000/")
                    print("  >>> [2] AI Assistant:       http://127.0.0.1:8000/assistant")
                    print("  >>> [3] 30-Clause Database: http://127.0.0.1:8000/database.html")
                    print("  >>> Opening Home Page in your browser now...")
                    print("="*65 + "\n")
                    webbrowser.open("http://127.0.0.1:8000/")
                    return
        except Exception:
            pass
    print("[VakeelLink] Server startup took longer than expected. Please open http://127.0.0.1:8000 manually.")

if __name__ == "__main__":
    browser_thread = threading.Thread(target=wait_and_open_browser, daemon=True)
    browser_thread.start()

    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, log_level="info")
