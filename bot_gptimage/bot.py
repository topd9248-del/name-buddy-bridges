import asyncio, re, os, time, threading, urllib.request
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from http.server import HTTPServer, BaseHTTPRequestHandler

API_ID = 28074212
API_HASH = "b18dae908474a377684922f3e9d5b795"
BOT_TOKEN = "8817226146:AAEV_XMkpcTw4-jlV22X3-04uOe3-9TwYPQ"

SESSIONS = [
    "1AZWarzsBu4STAQEQjoPhdDEN4XfnBqKQzWmgw8F8nUVt6TQx8101RCp0oxrhwcg1x4sq7rjlV2xWVl6ScaQrv2jXU8DyRjTfPIFeYEQpRVncpEdEbwcliu_NAiMzpgxZd4fPNoCcQ1i4-EmQqBdQPYX90VokgQaO-G6iKP8zuSGzm4AChajII3Ush6K8Z27uJQGl7dr4gCLWV7IsgEkUtXeNT8Yz8sMdBW9whSQBZn3btCTsWHI1XUY3PztsbIyFczAgYvROlyOGzVVueiqztB1SDqMNcojcWRbpL08tmqQb45jp00wflFX6UM_hfG1kJIB6q3dYuwbbo0_oxfItzqYs_OsTyrc=",
    "1AZWarzQBu4RpYUafm-K64e2G0lF5WWBiweaeiwIxCtz_lUlpxVpEul31rxKYrl1iM7Qy8Lm_IwHzVYMH8v9V2miRODgQ1MpdRd0FVFk71E3Ft5JQfH0dmePYe6i2JbFE5OyJK3DzwOIN0INJrzuc_7_KAuBVEg5rMbFwLoqFNiWLAKqQYjVOpPcnE5L4iZ3-a9pOSCmDmnHSKxxDpGJ4nXjWDAahpmOGreOYBfMl9y3z0Ok_NTBb9sOeRiBGDzixXwIOa0-5sbjDj0Xvy2w4HAxsBj6da9NFOVBu5mPZ69TEPotoZXofZPBDtpj85txK7O-KObnQvBwh1WzOBXjLSiDVpZbzed4=",
    "1AZWarzkBu2YBGExnst_V3sZheBKHyC6Vf1wWslQ-zxnZEN_TB-KxzYII7McBJVl3oNFQUaBkcfiFiqwy5vC5EiPvfGRsJUevjZpC0-fr-JZ3RyAGe7U7UZHowjh0jHheV826KHdyWQ2QZoJvIyT0gm4No3M6kxaO-WGd-Pb1s-jmrnx1k_MlvXXHAmTsQBSJmeegB7nLrZW22BA9ToHaaQxYd1xN082CCGyNlATs-319BwGsSz7ct0lg1vnu8YDpp-3Jef0xG4e7AMALoK5mSJKJktTq1i1D8lNi_AzJGElanlHtb_XilXraTo_vhNSWOJGgAY7EFANVg1Ku8N9_vKtwAxeX0Hs="
]
CLONE_BOT = "@GPT4Telegrambot"
CLONE_ID = 5896221213
CACHE = "@BuddyMovies_canal"
GRUPO = "@BuddyMovies_official"
BLOCK_WORDS = ['Tienes acceso a', 'modelos:', 'Gemini', 'consume', 'generaciones', '****', '—', 'Crea y edita',
               'Two models are available', 'Ready to get started', 'Send 1 to 10']

bot = TelegramClient('gptimage_bot', API_ID, API_HASH, retry_delay=5, auto_reconnect=True, timeout=15)
session_idx = 0
pending = {}
user_query = {}
client_pool = []

def next_client():
    global session_idx
    c = client_pool[session_idx % len(client_pool)]
    session_idx += 1
    return c

async def enviar_con_photo(client, texto):
    await client.send_message(CLONE_BOT, "/photo")
    await asyncio.sleep(1)
    await client.send_message(CLONE_BOT, texto)

async def init_clients():
    for sess in SESSIONS:
        c = TelegramClient(StringSession(sess), API_ID, API_HASH, retry_delay=5, auto_reconnect=True, timeout=15)
        await c.start()
        client_pool.append(c)
    print(f"✅ {len(client_pool)} clientes listos")

async def setup_client_handler(client):
    @client.on(events.NewMessage)
    async def on_new(event):
        m = event.message
        chat = await event.get_chat()
        if getattr(chat, 'id', 0) != CLONE_ID: return
        for uid, cid in list(pending.items()):
            cid = GRUPO
            
            if m.text and ("Has alcanzado tu límite" in m.text or "límite semanal" in m.text or 
                          "weekly limit" in m.text or "reached your" in m.text):
                c2 = next_client()
                await enviar_con_photo(c2, user_query.get(uid, "imagen"))
                await bot.send_message(cid, "🔄 Cambiando a otra sesión...")
                return
            
            if m.media or m.photo or m.video or m.document:
                cached = await client.send_file(CACHE, m.media or m.photo or m.video or m.document,
                    caption=(m.text or "") + "\n\n➠ @BuddyMovies_canal 🎬\n➠ @BuddyMovies_official 💬")
                link = f"https://t.me/{CACHE[1:]}/{cached.id}"
                await bot.send_message(cid,
                    f"🤖 **¡Aquí está tu imagen!**\n\n📝 {user_query.get(uid, 'imagen')}\n\n🔗 {link}",
                    buttons=[[Button.url("🎥 VER IMAGEN", link)]])
                return
            
            if m.text and ("Elige un servicio" in m.text or "Choose a service" in m.text or "Tendencias de Foto" in m.text):
                for row in m.buttons:
                    for btn in row:
                        if btn.text and "Nano Banana" in btn.text:
                            await btn.click()
                            return
            
            if m.text:
                text = m.text
                if any(kw in text for kw in BLOCK_WORDS): return
                if len(text.strip()) < 5: return
                await bot.send_message(cid, text)

    @client.on(events.MessageEdited)
    async def on_edit(event):
        m = event.message
        chat = await event.get_chat()
        if getattr(chat, 'id', 0) != CLONE_ID: return
        for uid, cid in list(pending.items()):
            cid = GRUPO
            
            if m.text and ("weekly limit" in m.text or "reached your" in m.text or "Has alcanzado" in m.text):
                c2 = next_client()
                await enviar_con_photo(c2, user_query.get(uid, "imagen"))
                await bot.send_message(cid, "🔄 Cambiando a otra sesión...")
                return
            
            if m.text and m.buttons:
                text = m.text
                if any(kw in text for kw in BLOCK_WORDS): return
                await bot.send_message(cid, text)

@bot.on(events.NewMessage)
async def on_user(event):
    if event.out: return
    uid = event.sender_id
    pending[uid] = event.chat_id
    user_query[uid] = event.message.text if event.message.text else "imagen"
    client = next_client()
    await enviar_con_photo(client, event.message.text)

@bot.on(events.CallbackQuery)
async def on_click(event):
    data = event.data.decode() if isinstance(event.data, bytes) else event.data
    for client in client_pool:
        async for m in client.iter_messages(CLONE_BOT, limit=10):
            if m.buttons:
                for row in m.buttons:
                    for btn in row:
                        bd = btn.data.decode() if isinstance(btn.data, bytes) else btn.data
                        if bd == data:
                            await event.answer("⚡")
                            await btn.click()
                            return
    await event.answer("⏳")

async def main():
    await init_clients()
    for client in client_pool:
        await setup_client_handler(client)
    await bot.start(bot_token=BOT_TOKEN)
    print(f"✅ GPT Image Generator en {GRUPO}")
    await bot.run_until_disconnected()

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
