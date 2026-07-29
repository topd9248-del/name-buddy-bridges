import asyncio, json, os, time, threading, urllib.request
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from http.server import HTTPServer, BaseHTTPRequestHandler

API_ID = 28074212
API_HASH = "b18dae908474a377684922f3e9d5b795"
BOT_TOKEN = "8712514693:AAFzKfLEUe0x7p3bdznPZInvKg8JwptXUYc"
SESSION = "1AZWarzsBu26nRF7Hs09KajSLH4ccYE0-ikzAFCJMv1ujaF5NeS_0-MdQjp-2uFqM3MH-cD-5cezRnI_HMuQVXIHOOMcQ7MmRLHpGxZRnJdJAyZ5WQl9E3YQMHErmWDjwepv2jiRjdVzTnvaC43ZeONw_ofHcPDUge-ZV3JeURsRcqa8FuC9eTJkQaU0WpFI2lKxFHZxj8E4DQBhbFIKrB3RnvevnZmq9JnOw4hRqfEw2zbbUlenB5Q-L9ljbQbFQy-aW1slvdvBV3CW4QVXI9sBMpf07TIh46QRpn_5oX7WpY7g8mMTW7n9Jkm_lcSkRnADE-7e-A0j4_EVofeUVYnBtkb5yOug="
GRUPO = "@BuddyMovies_official"
TIEMPO = 60

BOTS_A_ELIMINAR = ["@BuddyMovies_Bot", "@BuddyNotify_Bot"]

bot_client = TelegramClient('delete_bot', API_ID, API_HASH, retry_delay=5, auto_reconnect=True, timeout=15)
user_client = TelegramClient(StringSession(SESSION), API_ID, API_HASH, retry_delay=5, auto_reconnect=True, timeout=15)
grupo_entity = None
bots_ids = set()
mensajes_pendientes = {}

async def main():
    global grupo_entity
    
    await user_client.start()
    await bot_client.start(bot_token=BOT_TOKEN)
    print("✅ Auto Delete Bot activo")
    
    grupo_entity = await user_client.get_entity(GRUPO)
    
    # Obtener IDs de los bots a eliminar
    for bot_name in BOTS_A_ELIMINAR:
        try:
            entity = await user_client.get_entity(bot_name)
            bots_ids.add(entity.id)
            print(f"📌 {bot_name}: {entity.id}")
        except:
            print(f"⚠️ No encontrado: {bot_name}")
    
    # Handler: detectar mensajes de los bots
    @user_client.on(events.NewMessage(chats=GRUPO))
    async def on_msg(event):
        msg = event.message
        if msg.sender_id in bots_ids:
            mensajes_pendientes[msg.id] = time.time()
    
    @user_client.on(events.MessageEdited(chats=GRUPO))
    async def on_edit(event):
        msg = event.message
        if msg.sender_id in bots_ids:
            mensajes_pendientes[msg.id] = time.time()
    
    # Tarea: eliminar mensajes viejos
    async def eliminar_loop():
        while True:
            ahora = time.time()
            a_borrar = [mid for mid, ts in mensajes_pendientes.items() if ahora - ts >= TIEMPO]
            for mid in a_borrar:
                try:
                    await user_client.delete_messages(grupo_entity, mid)
                    del mensajes_pendientes[mid]
                except: pass
            await asyncio.sleep(2)
    
    asyncio.create_task(eliminar_loop())
    
    # Comandos del bot
    @bot_client.on(events.NewMessage(pattern='/status'))
    async def status(event):
        await event.reply(f"🗑️ Auto Delete\n⏱️ {TIEMPO}s\n📝 Pendientes: {len(mensajes_pendientes)}")
    
    @bot_client.on(events.NewMessage(pattern='/time'))
    async def time_cmd(event):
        global TIEMPO
        try:
            TIEMPO = int(event.text.split()[1])
            await event.reply(f"✅ Tiempo: {TIEMPO}s")
        except:
            await event.reply(f"❌ Uso: /time <segundos>")
    
    await asyncio.gather(bot_client.run_until_disconnected(), user_client.run_until_disconnected())

# Servidor HTTP para Render
class H(BaseHTTPRequestHandler):
    def do_GET(self): self.send_response(200); self.end_headers(); self.wfile.write(b"OK")
threading.Thread(target=lambda: HTTPServer(("0.0.0.0", int(os.environ.get("PORT",10000))), H).serve_forever(), daemon=True).start()

def keep_alive():
    while True:
        time.sleep(600)
        try: urllib.request.urlopen(f"http://localhost:{int(os.environ.get('PORT', 10000))}", timeout=5)
        except: pass
threading.Thread(target=keep_alive, daemon=True).start()

asyncio.run(main())
