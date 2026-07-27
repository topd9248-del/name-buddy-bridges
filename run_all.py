import subprocess, os, sys, time, threading, urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler

# Lista de bridges
BRIDGES = [
    "bridge_simple.py",
    "bridge_searchbot.py",
    "bridge_autofilter.py",
    "bridge_ltmovie.py",
    "bridge_angela.py",
    "bridge_apple.py",
]

processes = []

def start_bridge(script):
    """Inicia un bridge y lo reinicia si falla"""
    while True:
        try:
            print(f"🟢 Iniciando {script}...")
            p = subprocess.Popen([sys.executable, script], 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.STDOUT,
                                text=True)
            processes.append(p)
            
            # Leer output en tiempo real
            for line in p.stdout:
                print(f"[{script}] {line.strip()}")
            
            p.wait()
            print(f"🔴 {script} se detuvo. Reiniciando en 5s...")
            time.sleep(5)
        except Exception as e:
            print(f"❌ Error en {script}: {e}")
            time.sleep(10)

# ============================================
# SERVIDOR HTTP para mantener vivo Render
# ============================================
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def start_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"🌐 Servidor HTTP en puerto {port}")
    server.serve_forever()

# ============================================
# AUTO-PING
# ============================================
def auto_ping():
    port = int(os.environ.get("PORT", 10000))
    url = f"http://localhost:{port}"
    while True:
        time.sleep(600)
        try:
            urllib.request.urlopen(url, timeout=5)
            print("🔄 Ping OK")
        except:
            print("❌ Ping falló")

# ============================================
# MAIN
# ============================================
if __name__ == "__main__":
    print("🎬 INICIANDO 7 BRIDGES EN RENDER")
    print("=" * 40)
    
    # Iniciar servidor HTTP
    threading.Thread(target=start_server, daemon=True).start()
    
    # Iniciar auto-ping
    threading.Thread(target=auto_ping, daemon=True).start()
    
    # Iniciar cada bridge en su propio hilo
    for bridge in BRIDGES:
        if os.path.exists(bridge):
            threading.Thread(target=start_bridge, args=(bridge,), daemon=True).start()
            time.sleep(2)  # Esperar 2 seg entre cada inicio
    
    print("✅ TODOS LOS BRIDGES INICIADOS")
    print("=" * 40)
    
    # Mantener vivo el proceso principal
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("👋 Cerrando...")
