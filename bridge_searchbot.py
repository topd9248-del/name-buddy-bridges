import asyncio, re, os, time, threading, urllib.request, gc
from collections import OrderedDict
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from http.server import HTTPServer, BaseHTTPRequestHandler

API_ID = 28074212
API_HASH = "b18dae908474a377684922f3e9d5b795"
BOT_TOKEN = "8463069047:AAFw2frWMhqfELqxQzgplSODDC1kRuCJyII"
SESSION_READER = "1AZWarzQBuzncKy_mbzKcjlq0_XeKVuhMaiHWMBs3kkt9hmss9EcHTh9f9RtgQYkoDx4oXfLs8rnlwzNA8AHxmt47X2J3r4YJr0QVNVzX3meQKnDv1EKsnctVofcPlsHGuXPZutTrhs0-rtMFXO8TYMESuLbcu0BlENZDA6LVWzItTe17yMvgWexGLJMIyhO-yIrRxHr4838YkKxdxUflsSkjtSZIV8W4EWtrd6eOcTcZbaQyJEUT6jcyXrePbmfaOjMoOsx1PJF1dQisoPP_C-mRSHgp59Za4LmBM4EqQgzXeoPdUdXFRDkCJAfjzc3p6lnU7HqEtcKmm2EIzY43vj_iKSroOOo="
SEARCH_GROUP = "@TlgramMovieSearch_Bot"
CANAL = "@BuddyMovies_canal"
GRUPO = "@BuddyMovies_official"
FOOTER = "\n\n➠ @BuddyMovies_canal 🎬\n➠ @BuddyMovies_official 💬"

os.environ['PYTHONOPTIMIZE'] = '2'
gc.set_threshold(5000, 50, 50)
user_sessions = OrderedDict()
last_search_uid = None
button_map = {}
msg_map = {}

bot = TelegramClient('search_v3', API_ID, API_HASH, retry_delay=3, auto_reconnect=True, timeout=15)
reader = TelegramClient(StringSession(SESSION_READER), API_ID, API_HASH, retry_delay=3, auto_reconnect=True, timeout=15)

SKIP_BUTTONS = ['compartir bot', 'añadir a grupo', 'menú principal', 'share bot', 'add to group', 'main menu', 'inicio']

def filter_buttons(buttons):
    if not buttons: return None
    btns = []
    for row in buttons:
        r = []
        for btn in row:
            if btn.text and any(s in (btn.text or '').lower() for s in SKIP_BUTTONS): continue
            r.append(btn)
        if r: btns.append(r)
    return btns if btns else None

def clean_text(text):
    if not text: return ""
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'@(?!BuddyMovies)\w+', '', text)
    text = text.replace("¡Maldito! No te lo guardes solo para ti, comparte el bot para que todos lo conozcan", "¡Por favor! No te lo guardes solo para ti, comparte el bot para que todos lo conozcan 😊")
    text = text.replace("Busca películas, animes, series o doramas usando:", "Busca películas, animes, series o doramas usando.")
    text = text.replace("/search Nombre", "")
    text = text.replace("Ejemplo: /search Suisei no Gargantia", "")
    return text.strip()

SKIP_BUTTONS = ['compartir bot', 'añadir a grupo', 'menú principal', 'share bot', 'add to group', 'main menu', 'inicio']

def cache_buttons(msg, our_msg_id=None):
    if not msg or not msg.buttons: return None
    for row in msg.buttons:
        for btn in row:
            if btn.text and any(s in (btn.text or '').lower() for s in SKIP_BUTTONS): continue
            if btn.data:
                data = btn.data.decode() if isinstance(btn.data, bytes) else btn.data
                if our_msg_id:
                    button_map[(our_msg_id, data)] = (msg.id, msg.buttons.index(row), row.index(btn))
                button_map[data] = (msg.id, msg.buttons.index(row), row.index(btn))

@reader.on(events.NewMessage(chats=SEARCH_GROUP))
async def on_result(event):
    m = event.message
    if not m.sender or not m.sender.bot: return
    
    # AUTO-CLICKS
    if m.text and "selecciona un método" in m.text.lower():
        if m.buttons and m.buttons[0]: await m.buttons[0][0].click(); return
    if m.text and "selecciona un almacén" in m.text.lower():
        if m.buttons and m.buttons[0]: await m.buttons[0][0].click(); return
    
    if m.media:
        global last_search_uid
        uid = last_search_uid
        if uid and uid in user_sessions:
            s = user_sessions[uid]
            raw = clean_text(m.text or "") + FOOTER
            sent = await reader.send_file(CANAL, m.media, caption=raw)
            link = f"https://t.me/{CANAL[1:]}/{sent.id}"
            await bot.send_message(GRUPO, f"🎬 **{s['name']}**\n\n🔗 {link}", 
                buttons=[[Button.url("🎥 VER CONTENIDO", link)]], reply_to=s['rid'])

@reader.on(events.MessageEdited(chats=SEARCH_GROUP))
async def on_edit(event):
    m = event.message
    if not m.sender or not m.sender.bot or not m.text or not m.buttons: return
    text = clean_text(m.text)
    if m.id in msg_map:
        btns = filter_buttons(m.buttons)
        try:
            await bot.edit_message(GRUPO, msg_map[m.id], text=text[:4000], buttons=btns)
            cache_buttons(m, msg_map[m.id])
            return
        except: pass
    if user_sessions:
        uid = list(user_sessions.keys())[-1]
        s = user_sessions[uid]
        btns = filter_buttons(m.buttons)
        sent = await bot.send_message(GRUPO, text[:4000], buttons=btns, reply_to=s['rid'])
        if sent:
            msg_map[m.id] = sent.id
            cache_buttons(m, sent.id)

@bot.on(events.NewMessage)
async def on_user(event):
    if event.is_private:
        await event.reply("🎬 ¡BuddyPelis!\n👉 @BuddyMovies_official", buttons=[[Button.url("🎥 IR AL GRUPO", "https://t.me/BuddyMovies_official")]])
        return
    if event.out or not event.text: return
    q = event.text.strip()
    if len(q) < 2: return
    try: name = (await event.get_sender()).first_name or "Usuario"
    except: name = "Usuario"
    user_sessions[event.sender_id] = {'name': name, 'rid': event.message.id, 't': time.time()}
    global last_search_uid
    last_search_uid = event.sender_id
    await reader.send_message(SEARCH_GROUP, q)

@bot.on(events.CallbackQuery)
async def on_click(event):
    data = event.data.decode() if isinstance(event.data, bytes) else event.data
    if not data: return
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
    print(f"✅ @BuddyNotify_Bot")
    await asyncio.gather(bot.run_until_disconnected(), reader.run_until_disconnected())

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
