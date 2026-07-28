import subprocess, os, sys, time, threading, urllib.request, gc
from http.server import HTTPServer, BaseHTTPRequestHandler

print("🎬 3 BOTS", flush=True)
BRIDGES = ["bot_invite.py", "bridge_simple.py", "bridge_searchbot.py"]

def start(bot):
    while True:
        try:
            p = subprocess.Popen([sys.executable, bot], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            for line in p.stdout:
                print(f"[{bot[:8]}] {line.strip()}", flush=True)
            p.wait()
        except Exception as e:
            print(f"❌ {bot}: {e}", flush=True)
        time.sleep(3)
        gc.collect()

class H(BaseHTTPRequestHandler):
    def do_GET(self): self.send_response(200); self.end_headers(); self.wfile.write(b"OK")
    def do_HEAD(self): self.send_response(200); self.end_headers()

threading.Thread(target=lambda: HTTPServer(("0.0.0.0", int(os.environ.get("PORT",10000))), H).serve_forever(), daemon=True).start()

for b in BRIDGES:
    print(f"🟢 {b}", flush=True)
    threading.Thread(target=start, args=(b,), daemon=True).start()
    time.sleep(2)

print("✅ 3 BOTS VIVOS", flush=True)
while True:
    time.sleep(30)
    gc.collect()
