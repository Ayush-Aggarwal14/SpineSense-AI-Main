import subprocess
import http.server
import socketserver
import threading
import time
import os
import webbrowser

# Paths
PORT_SPLASH = 8000
PORT_STREAMLIT = 8501
SPLASH_DIR = os.path.join(os.path.dirname(__file__), "splash_screen")

streamlit_process = None

def start_streamlit():
    global streamlit_process
    print(f"[+] Starting Streamlit backend on port {PORT_STREAMLIT}...")
    streamlit_process = subprocess.Popen(
        ["streamlit", "run", "Posture_AG.py", "--server.port", str(PORT_STREAMLIT), "--server.headless", "true"],
        cwd=os.path.dirname(__file__)
    )

def start_splash_server():
    print(f"[+] Starting Splash Screen server on http://localhost:{PORT_SPLASH}...")
    os.chdir(SPLASH_DIR)
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT_SPLASH), Handler) as httpd:
        httpd.serve_forever()

if __name__ == "__main__":
    # Start Streamlit in background thread
    t1 = threading.Thread(target=start_streamlit, daemon=True)
    t1.start()
    
    # Wait a moment for Streamlit to initialize
    time.sleep(2)
    
    # Open the browser to the splash screen automatically
    print("\n>>> System Ready. Opening browser to Splash Screen... <<<")
    url = f"http://localhost:{PORT_SPLASH}"
    
    # Try to explicitly open in Google Chrome
    chrome_paths = [
        "C:/Program Files/Google/Chrome/Application/chrome.exe",
        "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"
    ]
    opened = False
    for path in chrome_paths:
        if os.path.exists(path):
            try:
                webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(path))
                webbrowser.get('chrome').open(url)
                opened = True
                break
            except Exception:
                pass
                
    if not opened:
        # Fallback to system default (Edge) if Chrome isn't found
        webbrowser.open(url)
    
    # Start the splash screen server on the main thread
    try:
        start_splash_server()
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        if streamlit_process:
            streamlit_process.terminate()
