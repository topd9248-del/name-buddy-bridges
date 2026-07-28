import subprocess, os, sys, time, threading, urllib.request, gc
from http.server import HTTPServer, BaseHTTPRequestHandler

print("🎬 2 BOTS", flush=True)
BRIDGES = ["bot_invite.py", "bridge_unico.py"]

def start(bot):
    while True:
        try:
            p = subprocess.Popen([sys.executable, bot], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            for line in p.stdout:
                print(f"[{bot[:8]}] {line.strip()}", flush=True)
            p.wait()
        except: pass
        time.sleep(5)
        gc.collect()

class H(BaseHTTPRequestHandler):
    def do_GET(self): self.send_response(200); self.end_headers(); self.wfile.write(b"OK")

threading.Thread(target=lambda: HTTPServer(("0.0.0.0", int(os.environ.get("PORT",10000))), H).serve_forever(), daemon=True).start()

for b in BRIDGES:
    threading.Thread(target=start, args=(b,), daemon=True).start()
    time.sleep(2)

while True:
    time.sleep(30)
    gc.collect()
