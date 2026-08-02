import asyncio, re, os, time, threading, urllib.request, gc
from collections import OrderedDict
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from http.server import HTTPServer, BaseHTTPRequestHandler

API_ID = 28074212
API_HASH = "b18dae908474a377684922f3e9d5b795"
BOT_TOKEN = "8724266934:AAEEzhSF2s6ZE8aR2zAHeJeGDzuhQWRCNdc"
SESSION_READER = "1AZWarzQBu5hWbHakw_V4c82HJA0uCNxvwdS_2JHHEVUbCghWQtCFrCbvfFEAMYTh1sCL3mMpTCJMmETKHXkmgBhynikL_1MTEXJfDlFxjnZQDXf1Glbd5w0HuyCQwEP6K_F2DnAS5vsGtH452l_HDS0uQMAGryhoTV7n5Tr9-5E1DmwY4CfKNV7uzYat15FQ6Nsm_vu8iPnQEwy5w5egiY_xnULhFKIkjWrr9gm7WS_OZbSwmEThy32o3I7zxIO__BiRmAFqPnICFo8OJR_FqU7JYoGvHeScnbgbOGU-bcmFUZrq_sFBbldOn1Y4G0TBw6gLeCCUjhwIh-td7KAjaDIRdaoI_lc="
SEARCH_GROUP = "@pooppuuui"
CANAL = "@BuddyMovies_canal"
GRUPO = "@BuddyMovies_official"
FOOTER = "\n\n➠ @BuddyMovies_canal 🎬\n➠ @BuddyMovies_official 💬"

os.environ['PYTHONOPTIMIZE'] = '2'
gc.set_threshold(5000, 50, 50)
user_sessions = OrderedDict()
button_map = {}
msg_map = {}
click_user = {}

bot = TelegramClient('buddy_v3', API_ID, API_HASH, retry_delay=3, auto_reconnect=True, timeout=15)
reader = TelegramClient(StringSession(SESSION_READER), API_ID, API_HASH, retry_delay=3, auto_reconnect=True, timeout=15)

def clean_text(text):
    if not text: return ""
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'@(?!BuddyMovies)\w+', '', text)
    text = text.replace("¡Maldito! No te lo guardes solo para ti, comparte el bot para que todos lo conozcan", "¡Por favor! No te lo guardes solo para ti, comparte el bot para que todos lo conozcan 😊")
    text = text.replace("Busca películas, animes, series o doramas usando:", "Busca películas, animes, series o doramas usando.")
    text = text.replace("/search Nombre", "")
    text = text.replace("Ejemplo: /search Suisei no Gargantia", "")
    return text.strip()

@reader.on(events.NewMessage(chats=SEARCH_GROUP))
async def on_result(event):
    m = event.message
    if not m.sender or not m.sender.bot: return
    if m.text and "buscando" in m.text.lower(): return
    
    if m.media:
        if click_user:
            uid = list(click_user.keys())[-1]
            s = click_user.pop(uid)
        elif user_sessions:
            uid = list(user_sessions.keys())[0]
            s = user_sessions.pop(uid)
        else:
            return
        raw = clean_text(m.text or "") + FOOTER
        sent = await reader.send_file(CANAL, m.media, caption=raw)
        link = f"https://t.me/{CANAL[1:]}/{sent.id}"
        await bot.send_message(GRUPO, f"🎬 **{s['name']}**\n\n🔗 {link}", buttons=[[Button.url("🎥 VER CONTENIDO", link)]], reply_to=s['rid'])
    
    elif m.text and m.buttons and user_sessions:
        uid = list(user_sessions.keys())[0]
        s = user_sessions.pop(uid)
        text = clean_text(m.text)
        sent = await bot.send_message(GRUPO, text[:4000], buttons=m.buttons, reply_to=s['rid'])
        if sent:
            msg_map[m.id] = sent.id
            for row in m.buttons:
                for btn in row:
                    if btn.data:
                        data = btn.data.decode() if isinstance(btn.data, bytes) else btn.data
                        button_map[(sent.id, data)] = (m.id, m.buttons.index(row), row.index(btn))
                        button_map[data] = (m.id, m.buttons.index(row), row.index(btn))

@reader.on(events.MessageEdited(chats=SEARCH_GROUP))
async def on_edit(event):
    m = event.message
    if not m.sender or not m.sender.bot or not m.text or not m.buttons: return
    text = clean_text(m.text)
    if m.id in msg_map:
        try: await bot.edit_message(GRUPO, msg_map[m.id], text=text[:4000], buttons=m.buttons); return
        except: pass

@bot.on(events.NewMessage)
async def on_user(event):
    if event.is_private:
        await event.reply("🎬 ¡BuddyPelis!\n👉 @BuddyMovies_official", buttons=[[Button.url("🎥 IR AL GRUPO", "https://t.me/BuddyMovies_official")]])
        return
    if event.out or not event.text: return
    
    # Verificar restricción
    try:
        import json, os
        if os.path.exists('pendientes.json'):
            with open('pendientes.json') as pf:
                if str(event.sender_id) in json.load(pf):
                    return
    except: pass
    q = event.text.strip()
    if len(q) < 2: return
    try: name = (await event.get_sender()).first_name or "Usuario"
    except: name = "Usuario"
    user_sessions[event.sender_id] = {'name': name, 'rid': event.message.id, 't': time.time()}
    await reader.send_message(SEARCH_GROUP, f"/search {q}")

@bot.on(events.CallbackQuery)
async def on_click(event):
    data = event.data.decode() if isinstance(event.data, bytes) else event.data
    if not data: return
    try: name = (await event.get_sender()).first_name or "Usuario"
    except: name = "Usuario"
    click_user[event.sender_id] = {'name': name, 'rid': event.message.id}
    key = (event.message_id, data)
    info = button_map.get(key) or button_map.get(data)
    if info:
        try:
            msgs = await reader.get_messages(SEARCH_GROUP, ids=[info[0]])
            if msgs and msgs[0].buttons:
                await event.answer("⚡")
                await msgs[0].buttons[info[1]][info[2]].click()
                return
        except: pass
    await event.answer("⏳ Expiró")

async def main():
    await reader.start()
    await bot.start(bot_token=BOT_TOKEN)
    print(f"✅ @BuddyMovies_Bot")
    await asyncio.gather(bot.run_until_disconnected(), reader.run_until_disconnected())

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
