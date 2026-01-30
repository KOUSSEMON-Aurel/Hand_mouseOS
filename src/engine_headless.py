import time
import signal
import sys
import threading
import cv2
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import sys
import os

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from src.engine import HandEngine
except ImportError:
    from engine import HandEngine

# Global frame buffer
output_frame = None
lock = threading.Lock()

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

class MJPEGHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global output_frame, lock
        if self.path == '/stream':
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=boundarydonotcross')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            try:
                while True:
                    with lock:
                        if output_frame is None:
                            continue
                        # Encode frame as JPEG
                        (flag, encodedImage) = cv2.imencode(".jpg", output_frame)
                        if not flag:
                            continue
                        
                    self.wfile.write(b'--boundarydonotcross\r\n')
                    self.send_header('Content-type', 'image/jpeg')
                    self.send_header('Content-length', str(len(encodedImage)))
                    self.end_headers()
                    self.wfile.write(encodedImage)
                    self.wfile.write(b'\r\n')
                    time.sleep(0.016) # ~60 FPS cap
            except Exception as e:
                # Client disconnected
                pass
        else:
            self.send_response(404)
            self.end_headers()

def start_server():
    server = ThreadingHTTPServer(('0.0.0.0', 5555), MJPEGHandler)
    print("🎥 MJPEG Server started on http://127.0.0.1:5555/stream")
    server.serve_forever()

def update_frame(img):
    global output_frame, lock
    with lock:
        output_frame = img.copy()

def main():
    print("🤖 Hand Mouse OS - Headless Engine Starting...")
    
    # 1. Start Engine
    engine = HandEngine(headless=True)
    engine.frame_callback = update_frame
    engine.start()

    # 2. Start MJPEG Server (Daemon thread)
    t = threading.Thread(target=start_server, daemon=True)
    t.start()

    def signal_handler(sig, frame):
        print("\n👋 Stopping Headless Engine...")
        engine.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("✅ Engine is running. Press Ctrl+C to stop.")
    
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
