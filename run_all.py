import subprocess, os, sys, time, threading, urllib.request, gc
from http.server import HTTPServer, BaseHTTPRequestHandler

print("🎬 3 BOTS", flush=True)

BRIDGES = ["bridge_invite.py", "bridge_simple.py", "bridge_searchbot.py"]

def start_bridge(script):
    while True:
        try:
            p = subprocess.Popen([sys.executable, script], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in p.stdout:
                if line.strip():
                    print(f"[{script[:8]}] {line.strip()}", flush=True)
            p.wait()
        except: pass
        time.sleep(5)
        gc.collect()

class H(BaseHTTPRequestHandler):
    def do_GET(self): self.send_response(200); self.end_headers(); self.wfile.write(b"OK")
    def do_HEAD(self): self.send_response(200); self.end_headers()

threading.Thread(target=lambda: HTTPServer(("0.0.0.0", int(os.environ.get("PORT",10000))), H).serve_forever(), daemon=True).start()

def ping():
    port = int(os.environ.get("PORT", 10000))
    while True:
        time.sleep(600)
        try: urllib.request.urlopen(f"http://localhost:{port}", timeout=5)
        except: pass
threading.Thread(target=ping, daemon=True).start()

for b in BRIDGES:
    threading.Thread(target=start_bridge, args=(b,), daemon=True).start()
    time.sleep(2)

while True:
    time.sleep(60)
    gc.collect()
