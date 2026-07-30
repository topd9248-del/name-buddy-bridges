import asyncio, json, os, time, urllib.request, threading
from telethon import TelegramClient, events, Button
from http.server import HTTPServer, BaseHTTPRequestHandler

API_ID = 28074212
API_HASH = "b18dae908474a377684922f3e9d5b795"
BOT_TOKEN = "8845956181:AAGRxHDEC9DVwNmDT-4ae3KOvDHA46ISRTY"
GRUPO_ID = -1002311102965
ADMIN_ID = 7771137226
META = 5
ENLACE = "https://t.me/BuddyMovies_official/1088"
ARCHIVO = "pendientes.json"

bot = TelegramClient('invite_bot', API_ID, API_HASH, retry_delay=5, auto_reconnect=True, timeout=15)
pendientes = json.load(open(ARCHIVO)) if os.path.exists(ARCHIVO) else {}
activo = False
solo_nuevos = False

def g(): json.dump(pendientes, open(ARCHIVO, 'w'))

@bot.on(events.ChatAction(chats=[GRUPO_ID]))
async def on_action(event):
    try: await event.delete()
    except: pass
    if event.user_joined and solo_nuevos:
        pendientes[str(event.user.id)] = 0; g()
        await bot.send_message(GRUPO_ID,
            f"🔒 Hola {event.user.first_name}, no puedes escribir aún.\n\n"
            f"Debes añadir {META} personas.\n\n📊 [{'⬜'*META}] 0/{META}\n\n👇",
            buttons=[[Button.url("💡 PASOS PARA ESCRIBIR 💡", ENLACE)]])
    if event.user_added and event.action_message and event.action_message.from_id:
        uid = str(event.action_message.from_id.user_id)
        if uid in pendientes:
            pendientes[uid] += 1; g()
            if pendientes[uid] >= META:
                del pendientes[uid]; g()
                try:
                    await bot.edit_permissions(GRUPO_ID, int(uid), send_messages=True)
                    await bot.send_message(GRUPO_ID, f"✅ {(await bot.get_entity(int(uid))).first_name}, ya puedes hablar.")
                except: pass

@bot.on(events.NewMessage(chats=[GRUPO_ID]))
async def on_msg(event):
    if event.out or event.sender_id == ADMIN_ID: return
    if event.text and event.text.startswith('/'): return
    uid = str(event.sender_id)
    if not activo or uid not in pendientes: return
    await event.delete()
    await bot.edit_permissions(GRUPO_ID, event.sender_id, send_messages=False)
    c = pendientes[uid]
    name = (await event.get_sender()).first_name or "Usuario"
    await bot.send_message(GRUPO_ID,
        f"🔒 Hola {name}, no puedes escribir aún.\n\n"
        f"Para poder escribir debes añadir a {META} personas al grupo.\n\n"
        f"📊 [{'🟩'*c}{'⬜'*(META-c)}] {c}/{META}\n\n"
        f"Sigue estos pasos 👇👇👇",
        buttons=[[Button.url("💡 PASOS PARA PODER ESCRIBIR 💡", ENLACE)]])

@bot.on(events.NewMessage(pattern='/reset', from_users=[ADMIN_ID]))
async def reset(event):
    global META, activo, solo_nuevos
    solo_nuevos = False
    try: META = int(event.text.split()[1])
    except: pass
    activo = True; pendientes.clear()
    async for m in bot.iter_participants(GRUPO_ID):
        if not m.bot and m.id != ADMIN_ID: pendientes[str(m.id)] = 0
    g()
    await event.reply(f"✅ {len(pendientes)} miembros, meta: {META}")

@bot.on(events.NewMessage(pattern='/lock', from_users=[ADMIN_ID]))
async def lock(event):
    global activo, solo_nuevos
    solo_nuevos = True; activo = True; pendientes.clear(); g()
    await event.reply(f"🔒 Solo nuevos, meta: {META}")

@bot.on(events.NewMessage(pattern='/free', from_users=[ADMIN_ID]))
async def free(event):
    global activo, solo_nuevos
    activo = False; solo_nuevos = False; pendientes.clear(); g()
    async for m in bot.iter_participants(GRUPO_ID):
        if not m.bot: await bot.edit_permissions(GRUPO_ID, m.id, send_messages=True)
    await event.reply("🔓 Libre")

@bot.on(events.NewMessage(pattern='/panel', from_users=[ADMIN_ID]))
async def panel(event):
    modo = "Solo nuevos" if solo_nuevos else ("ON" if activo else "OFF")
    await event.reply(f"⚙️ {modo} | Meta:{META} | Bloqueados:{len(pendientes)}")

async def main():
    await bot.start(bot_token=BOT_TOKEN)
    print("✅ Invite")
    await bot.run_until_disconnected()

class H(BaseHTTPRequestHandler):
    def do_GET(self): self.send_response(200); self.end_headers(); self.wfile.write(b"OK")
threading.Thread(target=lambda: HTTPServer(("0.0.0.0", int(os.environ.get("PORT",10000))), H).serve_forever(), daemon=True).start()

def keep_alive():
    import urllib.request
    while True:
        time.sleep(600)
        try: urllib.request.urlopen(f"http://localhost:{int(os.environ.get('PORT', 10000))}", timeout=5)
        except: pass
threading.Thread(target=keep_alive, daemon=True).start()

asyncio.run(main())
