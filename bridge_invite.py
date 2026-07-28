import asyncio, json, os, time, urllib.request
from telethon import TelegramClient, events, Button
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

API_ID = 28074212
API_HASH = "b18dae908474a377684922f3e9d5b795"
BOT_TOKEN = "8845956181:AAGRxHDEC9DVwNmDT-4ae3KOvDHA46ISRTY"
GRUPO_ID = -1002311102965
ADMIN_ID = 7771137226
META = 5
ENLACE = "https://t.me/BuddyMovies_official/1088"

bot = TelegramClient('invite_bot', API_ID, API_HASH, retry_delay=3, auto_reconnect=True, timeout=15)
pendientes = {}
activo = False
solo_nuevos = False
archivo = "pendientes.json"
avisos = {}

if os.path.exists(archivo):
    with open(archivo) as f: pendientes = json.load(f)

def guardar():
    with open(archivo, 'w') as f: json.dump(pendientes, f)

@bot.on(events.ChatAction(chats=[GRUPO_ID]))
async def chat_action(event):
    try: await event.delete()
    except: pass
    
    if event.user_joined and solo_nuevos:
        uid = str(event.user.id)
        pendientes[uid] = 0
        guardar()
        name = event.user.first_name or "Usuario"
        msg = await bot.send_message(GRUPO_ID,
            f"👤 {name}, para participar necesitas añadir {META} personas.\n📊 0/{META}",
            buttons=[[Button.url("💡 ¿Cómo se hace?", ENLACE)]])
        avisos[uid] = msg.id
    
    if event.user_added and event.action_message and event.action_message.from_id:
        uid = str(event.action_message.from_id.user_id)
        if uid in pendientes:
            pendientes[uid] += 1
            guardar()
            if pendientes[uid] >= META:
                del pendientes[uid]
                guardar()
                try:
                    ent = await bot.get_entity(int(uid))
                    await bot.edit_permissions(GRUPO_ID, int(uid), send_messages=True)
                    await bot.send_message(GRUPO_ID, f"✅ {ent.first_name}, ya puedes hablar.")
                    if uid in avisos:
                        try: await bot.delete_messages(GRUPO_ID, avisos[uid])
                        except: pass
                        del avisos[uid]
                except: pass

@bot.on(events.NewMessage(chats=[GRUPO_ID]))
async def filtrar(event):
    if event.out or event.sender_id == ADMIN_ID: return
    if event.text and event.text.startswith('/'): return
    uid = str(event.sender_id)
    if not activo or uid not in pendientes: return
    
    await event.delete()
    await bot.edit_permissions(GRUPO_ID, event.sender_id, send_messages=False)
    
    count = pendientes[uid]
    barra = "🟩" * count + "⬜" * (META - count)
    name = (await event.get_sender()).first_name or "Usuario"
    
    msg = await bot.send_message(GRUPO_ID,
        f"🔒 {name}, no puedes escribir aún.\n📌 Añade {META} personas.\n📊 [{barra}] {count}/{META}",
        buttons=[[Button.url("💡 ¿Cómo añadir?", ENLACE)]])
    avisos[uid] = msg.id

@bot.on(events.NewMessage(pattern='/reset', from_users=[ADMIN_ID]))
async def reset(event):
    if event.sender_id != ADMIN_ID: return
    global META, activo, solo_nuevos
    solo_nuevos = False
    try:
        p = event.text.split()
        if len(p) > 1: META = int(p[1])
    except: pass
    activo = True
    pendientes.clear()
    avisos.clear()
    async for m in bot.iter_participants(GRUPO_ID):
        if m.bot or m.id == ADMIN_ID: continue
        pendientes[str(m.id)] = 0
    guardar()
    await event.reply(f"✅ Restricción activada. {len(pendientes)} miembros deben añadir {META} personas.")

@bot.on(events.NewMessage(pattern='/lock', from_users=[ADMIN_ID]))
async def lock(event):
    if event.sender_id != ADMIN_ID: return
    global activo, solo_nuevos
    solo_nuevos = True
    activo = True
    pendientes.clear()
    avisos.clear()
    guardar()
    await event.reply(f"🔒 Solo nuevos deberán añadir {META} personas.")

@bot.on(events.NewMessage(pattern='/free', from_users=[ADMIN_ID]))
async def free(event):
    if event.sender_id != ADMIN_ID: return
    global activo, solo_nuevos
    activo = False
    solo_nuevos = False
    pendientes.clear()
    avisos.clear()
    guardar()
    c = 0
    async for m in bot.iter_participants(GRUPO_ID):
        if m.bot or m.id == ADMIN_ID: continue
        try: await bot.edit_permissions(GRUPO_ID, m.id, send_messages=True); c += 1
        except: pass
    await event.reply(f"🔓 Libre. {c} miembros liberados.")

@bot.on(events.NewMessage(pattern='/panel', from_users=[ADMIN_ID]))
async def panel(event):
    if event.sender_id != ADMIN_ID: return
    modo = "Solo nuevos" if solo_nuevos else ("Activado" if activo else "Libre")
    await event.reply(f"⚙️ {modo} | Meta: {META} | Pendientes: {len(pendientes)}")

async def main():
    await bot.start(bot_token=BOT_TOKEN)
    print(f"✅ Bot restricción activo")
    await bot.run_until_disconnected()

class H(BaseHTTPRequestHandler):
    def do_GET(self): self.send_response(200); self.end_headers(); self.wfile.write(b"OK")
    def do_HEAD(self): self.send_response(200); self.end_headers()
def run_server():
    HTTPServer(("0.0.0.0", int(os.environ.get("PORT", 10000))), H).serve_forever()
threading.Thread(target=run_server, daemon=True).start()

def keep_alive():
    while True:
        time.sleep(600)
        try: urllib.request.urlopen(f"http://localhost:{int(os.environ.get('PORT', 10000))}", timeout=5)
        except: pass
threading.Thread(target=keep_alive, daemon=True).start()

asyncio.run(main())
