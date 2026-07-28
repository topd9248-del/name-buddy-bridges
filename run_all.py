import subprocess, os, sys, time, threading, urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler

print("🎬 INICIANDO 3 BOTS EN RENDER", flush=True)

BRIDGES = [
    "bridge_invite.py",
    "bridge_simple.py",
    "bridge_searchbot.py"
]

def start_bridge(script):
    while True:
        try:
            print(f"🟢 {script}...", flush=True)
            p = subprocess.Popen([sys.executable, script], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in p.stdout:
                print(f"[{script}] {line.strip()}", flush=True)
            p.wait()
            time.sleep(5)
        except Exception as e:
            print(f"❌ {script}: {e}", flush=True)
            time.sleep(10)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"OK")
    def do_HEAD(self):
        self.send_response(200); self.end_headers()

def start_server():
    HTTPServer(("0.0.0.0", int(os.environ.get("PORT", 10000))), Handler).serve_forever()

def auto_ping():
    port = int(os.environ.get("PORT", 10000))
    while True:
        time.sleep(600)
        try: urllib.request.urlopen(f"http://localhost:{port}", timeout=5)
        except: pass

threading.Thread(target=start_server, daemon=True).start()
threading.Thread(target=auto_ping, daemon=True).start()

for bridge in BRIDGES:
    threading.Thread(target=start_bridge, args=(bridge,), daemon=True).start()
    time.sleep(2)

print("✅ 3 bots activos", flush=True)
while True:
    time.sleep(60)
