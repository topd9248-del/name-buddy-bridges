import subprocess, os, sys, time, threading, urllib.request, gc
from http.server import HTTPServer, BaseHTTPRequestHandler

print("🎬 INICIANDO", flush=True)

# Solo 1 bot para probar
BRIDGES = ["bot_invite.py"]

def start(bot):
    print(f"🟢 {bot}", flush=True)
    p = subprocess.Popen([sys.executable, bot], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in p.stdout:
        print(f"[{bot[:6]}] {line.strip()}", flush=True)

class H(BaseHTTPRequestHandler):
    def do_GET(self): self.send_response(200); self.end_headers(); self.wfile.write(b"OK")

threading.Thread(target=lambda: HTTPServer(("0.0.0.0", int(os.environ.get("PORT",10000))), H).serve_forever(), daemon=True).start()

for b in BRIDGES:
    t = threading.Thread(target=start, args=(b,))
    t.start()
    time.sleep(1)

print("✅ VIVO", flush=True)
while True:
    time.sleep(30)
