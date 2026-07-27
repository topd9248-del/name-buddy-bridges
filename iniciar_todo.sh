#!/bin/bash
clear
echo "🎬 CREANDO E INICIANDO BRIDGES..."
echo ""

# Crear bridge_simple.py
cat > ~/mi_bot/bridge_simple.py << 'ENDOFFILE'
import asyncio, re, os, threading, gc, time, urllib.request
from collections import OrderedDict
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from http.server import HTTPServer, BaseHTTPRequestHandler

API_ID = 28074212
API_HASH = "b18dae908474a377684922f3e9d5b795"
BOT_TOKEN = "8984212389:AAFZMh_ZQZm8DlIqPLvQEljnC1UPVtRJV-Q"
SESSION = "1AZWarzQBu5hWbHakw_V4c82HJA0uCNxvwdS_2JHHEVUbCghWQtCFrCbvfFEAMYTh1sCL3mMpTCJMmETKHXkmgBhynikL_1MTEXJfDlFxjnZQDXf1Glbd5w0HuyCQwEP6K_F2DnAS5vsGtH452l_HDS0uQMAGryhoTV7n5Tr9-5E1DmwY4CfKNV7uzYat15FQ6Nsm_vu8iPnQEwy5w5egiY_xnULhFKIkjWrr9gm7WS_OZbSwmEThy32o3I7zxIO__BiRmAFqPnICFo8OJR_FqU7JYoGvHeScnbgbOGU-bcmFUZrq_sFBbldOn1Y4G0TBw6gLeCCUjhwIh-td7KAjaDIRdaoI_lc="
SEARCH_GROUP = "@pooppuuui"
CANAL = "@BuddyMovies_canal"
GRUPO = "@BuddyMovies_official"

os.environ['PYTHONOPTIMIZE'] = '2'
gc.set_threshold(5000, 50, 50)
user_sessions = OrderedDict()
search_results = {}
button_map = {}
rate_limit = {}

bot = TelegramClient('buddy_bot2', API_ID, API_HASH, retry_delay=3, auto_reconnect=True, timeout=15)
user = TelegramClient(StringSession(SESSION), API_ID, API_HASH, retry_delay=3, auto_reconnect=True, timeout=15)

def clean_memory():
    now = time.time()
    expired = [k for k, v in user_sessions.items() if now - v.get('timestamp', 0) > 300]
    for k in expired: user_sessions.pop(k, None)
    if len(search_results) > 100:
        for k in list(search_results.keys())[:50]: search_results.pop(k, None)
    if len(button_map) > 1000:
        for k in list(button_map.keys())[:500]: button_map.pop(k, None)
    gc.collect()

def check_rate_limit(user_id):
    now = time.time()
    if user_id in rate_limit:
        recent = [t for t in rate_limit[user_id] if now - t < 60]
        rate_limit[user_id] = recent
        if len(recent) >= 15: return False
    else: rate_limit[user_id] = []
    rate_limit[user_id].append(now)
    return True

def cache_buttons(msg):
    if not msg or not msg.buttons: return None
    btns = []
    for row_idx, row in enumerate(msg.buttons):
        r = []
        for btn_idx, btn in enumerate(row):
            if btn.data:
                data = btn.data.decode() if isinstance(btn.data, bytes) else btn.data
                button_map[data] = (msg.id, row_idx, btn_idx)
                r.append(Button.inline(btn.text[:50], data[:64]))
            elif btn.url: r.append(Button.url(btn.text[:50], btn.url))
        if r: btns.append(r)
    return btns if btns else None

def replace_ads(text):
    if not text: return text
    text = text.replace("@TlgramMovieGroup_Bot", "@BuddyMovies_Bot")
    text = text.replace("@FILM_PARADIZE", "@BuddyMovies_official")
    text = text.replace("@RZXBOTZ", "@BuddyMovies_Bot")
    return text

@user.on(events.NewMessage(chats=SEARCH_GROUP))
async def on_result(event):
    clean_memory()
    m = event.message
    if not m.sender or not m.sender.bot: return
    if m.text and any(x in m.text.lower() for x in ["buscando", "espera", "recuerda usar", "ayúdanos", "compártelo", "gracias"]): return
    if m.media:
        if user_sessions:
            uid = list(user_sessions.keys())[-1]
            session = user_sessions[uid]
            name = session.get('name', 'Usuario')
            reply_to = session.get('reply_to')
            raw = replace_ads(m.text or "")
            sent = await user.send_file(CANAL, m.media, caption=raw)
            link = f"https://t.me/{CANAL[1:]}/{sent.id}"
            title = raw.split('\n')[0][:80] if raw else "Archivo"
            await bot.send_message(GRUPO, f"🎬 **{name}**\n📁 {title}\n\n🔗 {link}", buttons=[[Button.url("🎥 VER CONTENIDO", link)]], link_preview=False, reply_to=reply_to)
    elif m.text and m.buttons and len(m.text) > 20:
        buttons = cache_buttons(m)
        text = replace_ads(m.text)
        search_msg_id = m.id
        if search_msg_id in search_results:
            try: await bot.edit_message(search_results[m.id][0], search_results[m.id][1], text[:4000], buttons=buttons); return
            except: pass
        for uid, session in list(user_sessions.items()):
            try:
                sent = await bot.send_message(session.get('chat_id', GRUPO), text[:4000], buttons=buttons, reply_to=session.get('reply_to'))
                if sent: search_results[search_msg_id] = (session.get('chat_id', GRUPO), sent.id)
            except: pass
            break

@user.on(events.MessageEdited(chats=SEARCH_GROUP))
async def on_edit(event):
    clean_memory()
    m = event.message
    if not m.sender or not m.sender.bot or not m.text: return
    if any(x in m.text.lower() for x in ["buscando", "espera"]): return
    buttons = cache_buttons(m)
    text = replace_ads(m.text)
    search_msg_id = m.id
    if search_msg_id in search_results:
        try: await bot.edit_message(search_results[m.id][0], search_results[m.id][1], text[:4000], buttons=buttons); return
        except: pass
    for uid, session in list(user_sessions.items()):
        try:
            sent = await bot.send_message(session.get('chat_id', GRUPO), text[:4000], buttons=buttons, reply_to=session.get('reply_to'))
            if sent: search_results[search_msg_id] = (session.get('chat_id', GRUPO), sent.id)
        except: pass
        break

@bot.on(events.NewMessage)
async def on_user_msg(event):
    clean_memory()
    if event.is_private:
        await event.reply("🎬 <b>¡BuddyPelis!</b>\n\n📽️ <b>+5 millones de películas y series</b>\n🔍 Busca sin límites en el grupo\n\n👉 <b>Únete:</b> @BuddyMovies_official", buttons=[[Button.url("🎥 IR AL GRUPO", "https://t.me/BuddyMovies_official")]], link_preview=False)
        return
    if event.out or not event.text: return
    q = event.text.strip()
    if len(q) < 2 or q.startswith("/"): return
    if not check_rate_limit(event.sender_id):
        try: await event.reply("⏳ Espera un momento...")
        except: pass
        return
    try: sender = await bot.get_entity(event.sender_id); name = sender.first_name or "Usuario"
    except: name = "Usuario"
    user_sessions[event.sender_id] = {'name': name, 'chat_id': event.chat_id, 'reply_to': event.message.id, 'timestamp': time.time()}
    button_map.clear()
    sent = await user.send_message(SEARCH_GROUP, f"/search {q}")
    user_sessions[event.sender_id]['search_msg_id'] = sent.id

@bot.on(events.CallbackQuery)
async def on_click(event):
    data = event.data.decode() if isinstance(event.data, bytes) else event.data
    if not data: return
    if data in button_map:
        try:
            msgs = await user.get_messages(SEARCH_GROUP, ids=[button_map[data][0]])
            if msgs and msgs[0].buttons:
                await event.answer("⚡")
                await msgs[0].buttons[button_map[data][1]][button_map[data][2]].click()
                return
        except: pass
    try:
        msgs = await user.get_messages(SEARCH_GROUP, limit=50)
        for m in msgs:
            if m.buttons:
                for row in m.buttons:
                    for btn in row:
                        if (btn.data.decode() if isinstance(btn.data, bytes) else btn.data) == data:
                            await event.answer("⚡"); await btn.click(); return
    except: pass
    await event.answer("⏳ Expiró")

async def heartbeat():
    while True:
        await asyncio.sleep(180)
        try: await bot.get_me(); await user.get_me(); clean_memory()
        except: pass

async def main():
    await user.start(); await bot.start(bot_token=BOT_TOKEN)
    print(f"✅ @BuddyMovies_Bot → {GRUPO}")
    asyncio.create_task(heartbeat())
    await asyncio.gather(bot.run_until_disconnected(), user.run_until_disconnected())

class H(BaseHTTPRequestHandler):
    def do_GET(self): self.send_response(200); self.end_headers(); self.wfile.write(b"OK")
    def do_HEAD(self): self.send_response(200); self.end_headers()
def run_server(): HTTPServer(("0.0.0.0", int(os.environ.get("PORT", 10000))), H).serve_forever()
threading.Thread(target=run_server, daemon=True).start()

def keep_alive():
    while True:
        time.sleep(600)
        try: urllib.request.urlopen(f"http://localhost:{int(os.environ.get('PORT', 10000))}", timeout=5)
        except: pass
threading.Thread(target=keep_alive, daemon=True).start()

asyncio.run(main())
ENDOFFILE
echo "✅ 1/7"

# Crear bridge_searchbot.py
cat > ~/mi_bot/bridge_searchbot.py << 'ENDOFFILE'
import asyncio, re, os, threading, gc, time, urllib.request
from collections import OrderedDict
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from http.server import HTTPServer, BaseHTTPRequestHandler

API_ID = 28074212
API_HASH = "b18dae908474a377684922f3e9d5b795"
BOT_TOKEN = "8463069047:AAGeZg0IQd-1-Mv3ubxqnwZY1oJgxio9hr8"
SESSION = "1AZWarzQBuzncKy_mbzKcjlq0_XeKVuhMaiHWMBs3kkt9hmss9EcHTh9f9RtgQYkoDx4oXfLs8rnlwzNA8AHxmt47X2J3r4YJr0QVNVzX3meQKnDv1EKsnctVofcPlsHGuXPZutTrhs0-rtMFXO8TYMESuLbcu0BlENZDA6LVWzItTe17yMvgWexGLJMIyhO-yIrRxHr4838YkKxdxUflsSkjtSZIV8W4EWtrd6eOcTcZbaQyJEUT6jcyXrePbmfaOjMoOsx1PJF1dQisoPP_C-mRSHgp59Za4LmBM4EqQgzXeoPdUdXFRDkCJAfjzc3p6lnU7HqEtcKmm2EIzY43vj_iKSroOOo="
SEARCH_GROUP = "@TlgramMovieSearch_Bot"
CANAL = "@BuddyMovies_canal"
GRUPO = "@BuddyMovies_official"

os.environ['PYTHONOPTIMIZE'] = '2'
gc.set_threshold(5000, 50, 50)
user_sessions = OrderedDict()
search_results = {}
button_map = {}
rate_limit = {}

bot = TelegramClient('search_bridge2', API_ID, API_HASH, retry_delay=3, auto_reconnect=True, timeout=15)
user = TelegramClient(StringSession(SESSION), API_ID, API_HASH, retry_delay=3, auto_reconnect=True, timeout=15)
SKIP_BUTTONS = ['compartir bot', 'añadir a grupo', 'menú principal', 'share bot', 'add to group', 'main menu']

def clean_memory():
    now = time.time()
    expired = [k for k, v in user_sessions.items() if now - v.get('timestamp', 0) > 300]
    for k in expired: user_sessions.pop(k, None)
    if len(search_results) > 100:
        for k in list(search_results.keys())[:50]: search_results.pop(k, None)
    if len(button_map) > 1000:
        for k in list(button_map.keys())[:500]: button_map.pop(k, None)
    gc.collect()

def check_rate_limit(user_id):
    now = time.time()
    if user_id in rate_limit:
        recent = [t for t in rate_limit[user_id] if now - t < 60]
        rate_limit[user_id] = recent
        if len(recent) >= 15: return False
    else: rate_limit[user_id] = []
    rate_limit[user_id].append(now)
    return True

def cache_buttons(msg):
    if not msg or not msg.buttons: return None
    btns = []
    for row_idx, row in enumerate(msg.buttons):
        r = []
        for btn_idx, btn in enumerate(row):
            if btn.text and any(s in btn.text.lower() for s in SKIP_BUTTONS): continue
            if btn.data:
                data = btn.data.decode() if isinstance(btn.data, bytes) else btn.data
                button_map[data] = (msg.id, row_idx, btn_idx)
                r.append(Button.inline(btn.text[:50], data[:64]))
            elif btn.url: r.append(Button.url(btn.text[:50], btn.url))
        if r: btns.append(r)
    return btns if btns else None

def replace_ads(text):
    if not text: return text
    text = text.replace("@TlgramMovieSearch_Bot", "@BuddyNotify_Bot")
    text = text.replace("@TlgramMovieGroup_Bot", "@BuddyMovies_Bot")
    text = text.replace("@MotorBusquedaBot", "@BuddyNotify_Bot")
    text = text.replace("Estrenos 2026", "@BuddyMovies_official")
    text = text.replace("@FILM_PARADIZE", "@BuddyMovies_official")
    text = text.replace("@RZXBOTZ", "@BuddyMovies_Bot")
    text = re.sub(r'https?://\S*terabox\S*', '', text)
    text = text.replace('https://1024terabox.com/s/1lYx-v4HO1gmW6-J2qZFEgw', '@BuddyMovies_official')
    text = text.rstrip('@BuddyNotify_Bot').rstrip()
    return text

@user.on(events.NewMessage(chats=SEARCH_GROUP))
async def on_result(event):
    clean_memory()
    m = event.message
    if not m.sender or not m.sender.bot: return
    if m.text and any(x in m.text.lower() for x in ["procesando", "espera", "maldito", "comparte", "terabox", "revisa el anuncio"]): return
    if m.media:
        if user_sessions:
            uid = list(user_sessions.keys())[-1]
            session = user_sessions[uid]
            name = session.get('name', 'Usuario')
            raw = replace_ads(m.text or "")
            sent = await user.send_file(CANAL, m.media, caption=raw)
            link = f"https://t.me/{CANAL[1:]}/{sent.id}"
            title = raw.split('\n')[0][:80] if raw else "Archivo"
            await bot.send_message(session.get('chat_id', GRUPO), f"🎬 **{name}**\n📁 {title}\n\n🔗 {link}", buttons=[[Button.url("🎥 VER CONTENIDO", link)]], link_preview=False)
    elif m.text and len(m.text) > 20:
        if 'no se encontraron' in m.text.lower() or 'no se encontró' in m.text.lower(): buttons = None
        else: buttons = cache_buttons(m)
        text = replace_ads(m.text)
        search_msg_id = m.id
        if search_msg_id in search_results:
            try: await bot.edit_message(search_results[m.id][0], search_results[m.id][1], text[:4000], buttons=buttons); return
            except: pass
        for uid, session in list(user_sessions.items()):
            try:
                sent = await bot.send_message(session.get('chat_id', GRUPO), text[:4000], buttons=buttons, reply_to=session.get('reply_to'))
                if sent: search_results[search_msg_id] = (session.get('chat_id', GRUPO), sent.id)
            except: pass
            break

@user.on(events.MessageEdited(chats=SEARCH_GROUP))
async def on_edit(event):
    clean_memory()
    m = event.message
    if not m.sender or not m.sender.bot or not m.text: return
    if any(x in m.text.lower() for x in ["procesando", "espera"]): return
    if 'no se encontraron' in m.text.lower() or 'no se encontró' in m.text.lower(): buttons = None
    else: buttons = cache_buttons(m)
    text = replace_ads(m.text)
    search_msg_id = m.id
    if search_msg_id in search_results:
        try: await bot.edit_message(search_results[m.id][0], search_results[m.id][1], text[:4000], buttons=buttons); return
        except: pass
    for uid, session in list(user_sessions.items()):
        try:
            sent = await bot.send_message(session.get('chat_id', GRUPO), text[:4000], buttons=buttons, reply_to=session.get('reply_to'))
            if sent: search_results[search_msg_id] = (session.get('chat_id', GRUPO), sent.id)
        except: pass
        break

@bot.on(events.NewMessage)
async def on_user_msg(event):
    clean_memory()
    if event.is_private:
        await event.reply("🎬 <b>¡BuddyPelis!</b>\n\n📽️ <b>+5 millones de películas y series</b>\n🔍 Busca sin límites en el grupo\n\n👉 <b>Únete:</b> @BuddyMovies_official", buttons=[[Button.url("🎥 IR AL GRUPO", "https://t.me/BuddyMovies_official")]], link_preview=False)
        return
    if event.out or not event.text: return
    q = event.text.strip()
    if len(q) < 2 or q.startswith("/"): return
    if not check_rate_limit(event.sender_id):
        try: await event.reply("⏳ Espera un momento...")
        except: pass
        return
    try: sender = await bot.get_entity(event.sender_id); name = sender.first_name or "Usuario"
    except: name = "Usuario"
    user_sessions[event.sender_id] = {'name': name, 'chat_id': event.chat_id, 'reply_to': event.message.id, 'timestamp': time.time()}
    button_map.clear()
    sent = await user.send_message(SEARCH_GROUP, q)
    user_sessions[event.sender_id]['search_msg_id'] = sent.id

@bot.on(events.CallbackQuery)
async def on_click(event):
    data = event.data.decode() if isinstance(event.data, bytes) else event.data
    if not data: return
    if data in button_map:
        try:
            msgs = await user.get_messages(SEARCH_GROUP, ids=[button_map[data][0]])
            if msgs and msgs[0].buttons:
                await event.answer("⚡")
                await msgs[0].buttons[button_map[data][1]][button_map[data][2]].click()
                return
        except: pass
    try:
        msgs = await user.get_messages(SEARCH_GROUP, limit=50)
        for m in msgs:
            if m.buttons:
                for row in m.buttons:
                    for btn in row:
                        if (btn.data.decode() if isinstance(btn.data, bytes) else btn.data) == data:
                            await event.answer("⚡"); await btn.click(); return
    except: pass
    await event.answer("⏳ Expiró")

async def heartbeat():
    while True:
        await asyncio.sleep(180)
        try: await bot.get_me(); await user.get_me(); clean_memory()
        except: pass

async def main():
    await user.start(); await bot.start(bot_token=BOT_TOKEN)
    print(f"✅ @BuddyNotify_Bot → {GRUPO}")
    asyncio.create_task(heartbeat())
    await asyncio.gather(bot.run_until_disconnected(), user.run_until_disconnected())

class H(BaseHTTPRequestHandler):
    def do_GET(self): self.send_response(200); self.end_headers(); self.wfile.write(b"OK")
    def do_HEAD(self): self.send_response(200); self.end_headers()
def run_server(): HTTPServer(("0.0.0.0", int(os.environ.get("PORT", 10000))), H).serve_forever()
threading.Thread(target=run_server, daemon=True).start()

def keep_alive():
    while True:
        time.sleep(600)
        try: urllib.request.urlopen(f"http://localhost:{int(os.environ.get('PORT', 10000))}", timeout=5)
        except: pass
threading.Thread(target=keep_alive, daemon=True).start()

asyncio.run(main())
ENDOFFILE
echo "✅ 2/7"

# Crear bridge_autofilter.py
cat > ~/mi_bot/bridge_autofilter.py << 'ENDOFFILE'
import asyncio, re, os, threading, gc, time, urllib.request
from collections import OrderedDict
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from http.server import HTTPServer, BaseHTTPRequestHandler

API_ID = 28074212
API_HASH = "b18dae908474a377684922f3e9d5b795"
BOT_TOKEN = "7690330806:AAFAemkor12n71UAPaoJcnAcnPI_R_Xqygs"
SESSION = "1AZWarzQBu2q3JnP8YtBiwtloyr8QVF6AOFug129qO5bNQIRLsvnGelrXXIRdVYezjgm0IJNH5d_3lIBSNTxBTQnSss_Oz_MQksUSw1883Vbx5O3RyUM6UhYxhPe9jNuCHFhfTPn3iwxlQ63tJiNJ_Dd7ndNYdDFKsnrnKDvOkGX6H6UZyABCKj25nq8MCp6LRs22lV-AkmmVkdPRwL2CF7bIosmIHnfOrA2VxO_8ozC-iB08xA19YEqQtbA6YxCcYVgQuJAAyqqRIhqtHSibUloyqzYiLGUX7wWKPjYOrGOI4X-_NJAmTlkIvtQQHwd1HKI6NVLjnLker7Nas0wwUja1lOCfpQI="
SEARCH_GROUP = "@AutoFilter_Robot"
CANAL = "@BuddyMovies_canal"
GRUPO = "@BuddyMovies_official"

os.environ['PYTHONOPTIMIZE'] = '2'
gc.set_threshold(5000, 50, 50)
user_sessions = OrderedDict()
search_results = {}
button_map = {}
rate_limit = {}

bot = TelegramClient('autofilter_prod', API_ID, API_HASH, retry_delay=3, auto_reconnect=True, timeout=15)
user = TelegramClient(StringSession(SESSION), API_ID, API_HASH, retry_delay=3, auto_reconnect=True, timeout=15)
BLOCK_URLS = ['LfvtadGw', 'terabox']

def clean_memory():
    now = time.time()
    expired = [k for k, v in user_sessions.items() if now - v.get('timestamp', 0) > 300]
    for k in expired: user_sessions.pop(k, None)
    if len(search_results) > 100:
        for k in list(search_results.keys())[:50]: search_results.pop(k, None)
    if len(button_map) > 1000:
        for k in list(button_map.keys())[:500]: button_map.pop(k, None)
    gc.collect()

def check_rate_limit(user_id):
    now = time.time()
    if user_id in rate_limit:
        recent = [t for t in rate_limit[user_id] if now - t < 60]
        rate_limit[user_id] = recent
        if len(recent) >= 15: return False
    else: rate_limit[user_id] = []
    rate_limit[user_id].append(now)
    return True

def cache_buttons(msg):
    if not msg or not msg.buttons: return None
    btns = []
    for row_idx, row in enumerate(msg.buttons):
        r = []
        for btn_idx, btn in enumerate(row):
            if btn.url and any(b in (btn.url or '') for b in BLOCK_URLS): continue
            if btn.data:
                data = btn.data.decode() if isinstance(btn.data, bytes) else btn.data
                button_map[data] = (msg.id, row_idx, btn_idx)
                r.append(Button.inline(btn.text[:50], data[:64]))
            elif btn.url: r.append(Button.url(btn.text[:50], btn.url))
        if r: btns.append(r)
    return btns if btns else None

def replace_ads(text):
    if not text: return text
    text = text.replace("@TlgramMovieGroup_Bot", "@BuddyMovies_Bot")
    text = text.replace("@FILM_PARADIZE", "@BuddyMovies_official")
    text = text.replace("@RZXBOTZ", "@BuddyMovies_Bot")
    return text

@user.on(events.NewMessage(chats=SEARCH_GROUP))
async def on_result(event):
    clean_memory()
    m = event.message
    if not m.sender or not m.sender.bot: return
    if m.text and any(x in m.text.lower() for x in ["save the file", "will be deleted", "select language"]): return
    if m.text and ("no results found" in m.text.lower() or "not available" in m.text.lower()):
        for uid, session in list(user_sessions.items()):
            try: await bot.send_message(session.get('chat_id', GRUPO), "❌ No se encontraron resultados.", reply_to=session.get('reply_to'))
            except: pass
            break
        return
    if m.media:
        if user_sessions:
            uid = list(user_sessions.keys())[-1]
            session = user_sessions[uid]
            name = session.get('name', 'Usuario')
            reply_to = session.get('reply_to')
            raw = replace_ads(m.text or "")
            sent = await user.send_file(CANAL, m.media, caption=raw)
            link = f"https://t.me/{CANAL[1:]}/{sent.id}"
            title = raw.split('\n')[0][:80] if raw else "Archivo"
            await bot.send_message(GRUPO, f"🎬 **{name}**\n📁 {title}\n\n🔗 {link}", buttons=[[Button.url("🎥 VER CONTENIDO", link)]], link_preview=False, reply_to=reply_to)
    elif m.text and len(m.text) > 20:
        buttons = cache_buttons(m)
        text = replace_ads(m.text)
        text = re.sub(r'Hey \*\*.*?\*\*!', '👋 **¡Hola!**', text)
        text = re.sub(r'Search Query:', '🔍 Búsqueda:', text)
        text = re.sub(r'Total Results:', '📊 Resultados:', text)
        text = re.sub(r'Page:', '📄 Página:', text)
        search_msg_id = m.id
        if search_msg_id in search_results:
            try: await bot.edit_message(search_results[m.id][0], search_results[m.id][1], text[:4000], buttons=buttons); return
            except: pass
        for uid, session in list(user_sessions.items()):
            try:
                sent = await bot.send_message(session.get('chat_id', GRUPO), text[:4000], buttons=buttons, reply_to=session.get('reply_to'))
                if sent: search_results[search_msg_id] = (session.get('chat_id', GRUPO), sent.id)
            except: pass
            break

@user.on(events.MessageEdited(chats=SEARCH_GROUP))
async def on_edit(event):
    clean_memory()
    m = event.message
    if not m.sender or not m.sender.bot or not m.text: return
    buttons = cache_buttons(m)
    text = replace_ads(m.text)
    text = re.sub(r'Hey \*\*.*?\*\*!', '👋 **¡Hola!**', text)
    text = re.sub(r'Search Query:', '🔍 Búsqueda:', text)
    text = re.sub(r'Total Results:', '📊 Resultados:', text)
    text = re.sub(r'Page:', '📄 Página:', text)
    search_msg_id = m.id
    if search_msg_id in search_results:
        try: await bot.edit_message(search_results[m.id][0], search_results[m.id][1], text[:4000], buttons=buttons); return
        except: pass
    for uid, session in list(user_sessions.items()):
        try:
            sent = await bot.send_message(session.get('chat_id', GRUPO), text[:4000], buttons=buttons, reply_to=session.get('reply_to'))
            if sent: search_results[search_msg_id] = (session.get('chat_id', GRUPO), sent.id)
        except: pass
        break

@bot.on(events.NewMessage)
async def on_user_msg(event):
    clean_memory()
    if event.is_private:
        await event.reply("🎬 <b>¡BuddyPelis!</b>\n\n📽️ <b>+5 millones de películas y series</b>\n🔍 Busca sin límites en el grupo\n\n👉 <b>Únete:</b> @BuddyMovies_official", buttons=[[Button.url("🎥 IR AL GRUPO", "https://t.me/BuddyMovies_official")]], link_preview=False)
        return
    if event.out or not event.text: return
    q = event.text.strip()
    if len(q) < 2 or q.startswith("/"): return
    if not check_rate_limit(event.sender_id):
        try: await event.reply("⏳ Espera un momento...")
        except: pass
        return
    try: sender = await bot.get_entity(event.sender_id); name = sender.first_name or "Usuario"
    except: name = "Usuario"
    user_sessions[event.sender_id] = {'name': name, 'chat_id': event.chat_id, 'reply_to': event.message.id, 'timestamp': time.time()}
    button_map.clear()
    await user.send_message(SEARCH_GROUP, q)

@bot.on(events.CallbackQuery)
async def on_click(event):
    data = event.data.decode() if isinstance(event.data, bytes) else event.data
    if not data: return
    if data in button_map:
        try:
            msgs = await user.get_messages(SEARCH_GROUP, ids=[button_map[data][0]])
            if msgs and msgs[0].buttons:
                await event.answer("⚡")
                await msgs[0].buttons[button_map[data][1]][button_map[data][2]].click()
                return
        except: pass
    try:
        msgs = await user.get_messages(SEARCH_GROUP, limit=50)
        for m in msgs:
            if m.buttons:
                for row in m.buttons:
                    for btn in row:
                        if (btn.data.decode() if isinstance(btn.data, bytes) else btn.data) == data:
                            await event.answer("⚡"); await btn.click(); return
    except: pass
    await event.answer("⏳ Expiró")

async def heartbeat():
    while True:
        await asyncio.sleep(180)
        try: await bot.get_me(); await user.get_me(); clean_memory()
        except: pass

async def main():
    await user.start(); await bot.start(bot_token=BOT_TOKEN)
    print(f"✅ @AutoFilter_Bridge → {GRUPO}")
    asyncio.create_task(heartbeat())
    await asyncio.gather(bot.run_until_disconnected(), user.run_until_disconnected())

class H(BaseHTTPRequestHandler):
    def do_GET(self): self.send_response(200); self.end_headers(); self.wfile.write(b"OK")
    def do_HEAD(self): self.send_response(200); self.end_headers()
def run_server(): HTTPServer(("0.0.0.0", int(os.environ.get("PORT", 10000))), H).serve_forever()
threading.Thread(target=run_server, daemon=True).start()

def keep_alive():
    while True:
        time.sleep(600)
        try: urllib.request.urlopen(f"http://localhost:{int(os.environ.get('PORT', 10000))}", timeout=5)
        except: pass
threading.Thread(target=keep_alive, daemon=True).start()

asyncio.run(main())
ENDOFFILE
echo "✅ 3/7"

# Crear bridge_ltmovie.py
cat > ~/mi_bot/bridge_ltmovie.py << 'ENDOFFILE'
import asyncio, re, os, threading, gc, time, urllib.request
from collections import OrderedDict
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from http.server import HTTPServer, BaseHTTPRequestHandler

API_ID = 28074212
API_HASH = "b18dae908474a377684922f3e9d5b795"
BOT_TOKEN = "8808014809:AAEacf05HWO2g4HFWDTlP8IC6lXMBxILqbM"
SESSION = "1AZWarzQBuw2Qy79iGpD5cWK5pf1LtqHo8f-gjYTl7G8c4wcEvAXuhRifBWgMyrQeXsW62Jpv2YbE3yQJJC1D520D4CPbkOHM5c9NUlDOaQNGDg4gbTzf00Ye6KlbLifZpgQI9Zk3SO9EeMJlq7MVvqUNUgMpCaxYl3oMcAhhqnzHPgMmdQR9epRSKMU6d_PeQ7NHThlpYHHYB5wpMBz2-IaajdMMXPB4-shgmIHGeh_BdQy6UArhkcLFaxCu-f60MK39MUzYq4UElN0aaSn7HuSfaszh5QlALJQe9AZrP1Jsa7UzErtsZ0JDsoMt6ujcvgpXCYu3xYQkNTQh1s7n-qb4y8uaQZU="
SEARCH_GROUP = "@Lt_Moviebot"
SEARCH_ID = 8504453537
CANAL = "@BuddyMovies_canal"
GRUPO = "@BuddyMovies_official"

os.environ['PYTHONOPTIMIZE'] = '2'
gc.set_threshold(5000, 50, 50)
user_sessions = OrderedDict()
search_results = {}
button_map = {}
msg_map = {}
rate_limit = {}

bot = TelegramClient('ltmovie_bridge', API_ID, API_HASH, retry_delay=3, auto_reconnect=True, timeout=15)
user = TelegramClient(StringSession(SESSION), API_ID, API_HASH, retry_delay=3, auto_reconnect=True, timeout=15)
FOOTER = "\n\n➠ 𝖫𝖺𝗍𝖾𝗌𝗍 𝖴𝗉𝗅𝗈𝖺𝖽𝗌: @BuddyMovies_official\n➠ 𝖡𝗈𝗍 𝖴𝗉𝖽𝖺𝗍𝖾𝗌: @BuddyMovies_Bot"
BLOCK_URLS = ['d-3RL7TJKnVlN2Nk', 'CM_Zone', 'f9RVIwfGDYo2NDM1', 'LfvtadGw', '+d-3RL7TJKnVlN2Nk', '+f9RVIwfGDYo2NDM1']

def clean_memory():
    now = time.time()
    expired = [k for k, v in user_sessions.items() if now - v.get('timestamp', 0) > 300]
    for k in expired: user_sessions.pop(k, None)
    if len(search_results) > 100:
        for k in list(search_results.keys())[:50]: search_results.pop(k, None)
    if len(button_map) > 1000:
        for k in list(button_map.keys())[:500]: button_map.pop(k, None)
    gc.collect()

def check_rate_limit(user_id):
    now = time.time()
    if user_id in rate_limit:
        recent = [t for t in rate_limit[user_id] if now - t < 60]
        rate_limit[user_id] = recent
        if len(recent) >= 15: return False
    else: rate_limit[user_id] = []
    rate_limit[user_id].append(now)
    return True

def replace_ads(text):
    if not text: return text
    text = text.replace("@TlgramMovieGroup_Bot", "@BuddyMovies_Bot")
    text = text.replace("@FILM_PARADIZE", "@BuddyMovies_official")
    text = re.sub(r'https?://t\.me/[^\s]+', '', text)
    text = re.sub(r'https?://[^\s]*terabox[^\s]*', '', text)
    return text

def build_buttons(m):
    btns = []
    for row_idx, row in enumerate(m.buttons):
        r = []
        for btn_idx, btn in enumerate(row):
            text = (btn.text or '').strip()
            if btn.url and any(b in (btn.url or '') for b in BLOCK_URLS): continue
            if btn.url and btn.url.startswith('http') and 't.me' not in btn.url: continue
            if text in ['\u200b', '\u200b ']:
                ds = str(btn.data) if btn.data else ''
                if 'lang' in ds: text = '🌐'
                elif 'qual' in ds: text = '🎞️'
                elif 'nxt' in ds: text = '▶️'
                elif 'pgkb' in ds: text = '📄'
                else: text = '▫️'
            elif not text and not btn.url: continue
            if btn.data:
                data = btn.data.decode() if isinstance(btn.data, bytes) else btn.data
                button_map[data] = (m.id, row_idx, btn_idx)
                r.append(Button.inline(text[:50], data))
            elif btn.url:
                r.append(Button.url(text[:50] if text else '🔗', btn.url))
        if r: btns.append(r)
    return btns if btns else None

@user.on(events.NewMessage(chats=SEARCH_GROUP))
async def on_result(event):
    clean_memory()
    m = event.message
    if m.sender_id != SEARCH_ID: return
    if not user_sessions: return
    uid = list(user_sessions.keys())[-1]
    s = user_sessions[uid]
    if m.media:
        caption = replace_ads(m.text or "") + FOOTER
        sent = await user.send_file(CANAL, m.media, caption=caption)
        link = f"https://t.me/{CANAL[1:]}/{sent.id}"
        await bot.send_message(GRUPO, f"🎬 **{s['name']}**\n\n🔗 {link}", buttons=[[Button.url("🎥 VER CONTENIDO", link)]], reply_to=s['reply_to'])
    elif m.text and m.buttons:
        btns = build_buttons(m)
        text = replace_ads(m.text)
        sent = await bot.send_message(GRUPO, text[:4000], buttons=btns, reply_to=s['reply_to'])
        if sent: msg_map[m.id] = sent.id

@user.on(events.MessageEdited(chats=SEARCH_GROUP))
async def on_edit(event):
    clean_memory()
    m = event.message
    if m.sender_id != SEARCH_ID: return
    if not m.text or not m.buttons: return
    if m.id in msg_map:
        btns = build_buttons(m)
        text = replace_ads(m.text)
        try: await bot.edit_message(GRUPO, msg_map[m.id], text[:4000], buttons=btns)
        except: pass

@bot.on(events.NewMessage)
async def on_user_msg(event):
    clean_memory()
    if event.is_private:
        await event.reply("🎬 <b>¡BuddyPelis!</b>\n\n📽️ <b>+5 millones de películas y series</b>\n🔍 Busca sin límites en el grupo\n\n👉 <b>Únete:</b> @BuddyMovies_official", buttons=[[Button.url("🎥 IR AL GRUPO", "https://t.me/BuddyMovies_official")]], link_preview=False)
        return
    if event.out or not event.text: return
    q = event.text.strip()
    if len(q) < 2 or q.startswith("/"): return
    if not check_rate_limit(event.sender_id):
        try: await event.reply("⏳ Espera un momento...")
        except: pass
        return
    try: s = await event.get_sender(); name = s.first_name if s else "Usuario"
    except: name = "Usuario"
    user_sessions[event.sender_id] = {'name': name, 'chat_id': event.chat_id, 'reply_to': event.message.id, 'timestamp': time.time()}
    button_map.clear(); msg_map.clear()
    await user.send_message(SEARCH_GROUP, q)

@bot.on(events.CallbackQuery)
async def on_click(event):
    data = event.data.decode() if isinstance(event.data, bytes) else event.data
    if not data: return
    if data in button_map:
        try:
            msgs = await user.get_messages(SEARCH_GROUP, ids=[button_map[data][0]])
            if msgs and msgs[0].buttons:
                btn = msgs[0].buttons[button_map[data][1]][button_map[data][2]]
                await event.answer("⚡"); await btn.click(); return
        except: pass
    try:
        msgs = await user.get_messages(SEARCH_GROUP, limit=50)
        for m in msgs:
            if m.buttons:
                for row in m.buttons:
                    for btn in row:
                        bd = btn.data.decode() if isinstance(btn.data, bytes) else btn.data
                        if bd == data:
                            await event.answer("⚡"); await btn.click(); return
    except: pass
    await event.answer("⏳ Expiró")

async def heartbeat():
    while True:
        await asyncio.sleep(180)
        try: await bot.get_me(); await user.get_me(); clean_memory()
        except: pass

async def main():
    await user.start(); await bot.start(bot_token=BOT_TOKEN)
    print(f"✅ @Lt_Moviebot Bridge → {GRUPO}")
    asyncio.create_task(heartbeat())
    await asyncio.gather(bot.run_until_disconnected(), user.run_until_disconnected())

class H(BaseHTTPRequestHandler):
    def do_GET(self): self.send_response(200); self.end_headers(); self.wfile.write(b"OK")
    def do_HEAD(self): self.send_response(200); self.end_headers()
def run_server(): HTTPServer(("0.0.0.0", int(os.environ.get("PORT", 10000))), H).serve_forever()
threading.Thread(target=run_server, daemon=True).start()

def keep_alive():
    while True:
        time.sleep(600)
        try: urllib.request.urlopen(f"http://localhost:{int(os.environ.get('PORT', 10000))}", timeout=5)
        except: pass
threading.Thread(target=keep_alive, daemon=True).start()

asyncio.run(main())
ENDOFFILE
echo "✅ 4/7"

# Crear bridge_angela.py
cat > ~/mi_bot/bridge_angela.py << 'ENDOFFILE'
import asyncio, re, os, threading, gc, time, urllib.request
from collections import OrderedDict
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

API_ID = 28074212
API_HASH = "b18dae908474a377684922f3e9d5b795"
BOT_TOKEN = "8894814453:AAGAuF3cjETqYt_mY2os9raZgMxSZtFqD_E"
SESSION = "1AZWarzQBuw2Qy79iGpD5cWK5pf1LtqHo8f-gjYTl7G8c4wcEvAXuhRifBWgMyrQeXsW62Jpv2YbE3yQJJC1D520D4CPbkOHM5c9NUlDOaQNGDg4gbTzf00Ye6KlbLifZpgQI9Zk3SO9EeMJlq7MVvqUNUgMpCaxYl3oMcAhhqnzHPgMmdQR9epRSKMU6d_PeQ7NHThlpYHHYB5wpMBz2-IaajdMMXPB4-shgmIHGeh_BdQy6UArhkcLFaxCu-f60MK39MUzYq4UElN0aaSn7HuSfaszh5QlALJQe9AZrP1Jsa7UzErtsZ0JDsoMt6ujcvgpXCYu3xYQkNTQh1s7n-qb4y8uaQZU="
SEARCH_GROUP = "@Angela2_moviebot"
SEARCH_ID = 8143714699
CANAL = "@BuddyMovies_canal"
GRUPO = "@BuddyMovies_official"

os.environ['PYTHONOPTIMIZE'] = '2'
gc.set_threshold(5000, 50, 50)
user_sessions = OrderedDict()
button_map = {}
msg_map = {}
rate_limit = {}

bot = TelegramClient('angela_bridge', API_ID, API_HASH, retry_delay=3, auto_reconnect=True, timeout=15)
user = TelegramClient(StringSession(SESSION), API_ID, API_HASH, retry_delay=3, auto_reconnect=True, timeout=15)
FOOTER = "\n\n➠ 𝖫𝖺𝗍𝖾𝗌𝗍 𝖴𝗉𝗅𝗈𝖺𝖽𝗌: @BuddyMovies_official\n➠ 𝖡𝗈𝗍 𝖴𝗉𝖽𝖺𝗍𝖾𝗌: @BuddyMovies_Bot"

def clean_memory():
    now = time.time()
    expired = [k for k, v in user_sessions.items() if now - v.get('timestamp', 0) > 300]
    for k in expired: user_sessions.pop(k, None)
    if len(button_map) > 2000:
        for k in list(button_map.keys())[:1000]: button_map.pop(k, None)
    gc.collect()

def check_rate_limit(user_id):
    now = time.time()
    if user_id in rate_limit:
        recent = [t for t in rate_limit[user_id] if now - t < 60]
        rate_limit[user_id] = recent
        if len(recent) >= 15: return False
    else: rate_limit[user_id] = []
    rate_limit[user_id].append(now)
    return True

def replace_ads(text):
    if not text: return text
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'.*Updates\s*:.*', '', text)
    text = re.sub(r'.*auto.delete.*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'.*copyright.*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
    return text.strip()

def build_buttons(m, our_msg_id):
    btns = []
    for row_idx, row in enumerate(m.buttons):
        r = []
        for btn_idx, btn in enumerate(row):
            text = (btn.text or '').strip()
            if btn.url and 'start=' in btn.url:
                parsed = urlparse(btn.url)
                params = parse_qs(parsed.query)
                start_data = params.get('start', [''])[0]
                if start_data:
                    fake_data = f"dl_{start_data[:40]}"
                    button_map[(our_msg_id, fake_data)] = (m.id, row_idx, btn_idx, start_data)
                    r.append(Button.inline(text[:50] if text else '📥', fake_data))
                continue
            if btn.url: continue
            if btn.data:
                data = btn.data.decode() if isinstance(btn.data, bytes) else btn.data
                button_map[(our_msg_id, data)] = (m.id, row_idx, btn_idx, None)
                if text in ['\u200b', '\u200b ']:
                    ds = str(btn.data)
                    if 'lang' in ds: text = '🌐'
                    elif 'qual' in ds: text = '🎞️'
                    elif 'next' in ds: text = '▶️'
                    elif 'buttons' in ds: text = '📄'
                    else: text = '▫️'
                r.append(Button.inline(text[:50], data))
        if r: btns.append(r)
    return btns if btns else None

@user.on(events.NewMessage(chats=SEARCH_GROUP))
async def on_result(event):
    clean_memory()
    m = event.message
    if m.sender_id != SEARCH_ID: return
    if not user_sessions: return
    uid = list(user_sessions.keys())[-1]
    s = user_sessions[uid]
    if m.media:
        caption = replace_ads(m.text or "") + FOOTER
        sent = await user.send_file(CANAL, m.media, caption=caption)
        link = f"https://t.me/{CANAL[1:]}/{sent.id}"
        await bot.send_message(GRUPO, f"🎬 **{s['name']}**\n\n🔗 {link}", buttons=[[Button.url("🎥 VER CONTENIDO", link)]], reply_to=s['reply_to'])
    elif m.text and m.buttons:
        sent = await bot.send_message(GRUPO, "...", reply_to=s['reply_to'])
        our_id = sent.id
        btns = build_buttons(m, our_id)
        text = replace_ads(m.text)
        await bot.edit_message(GRUPO, our_id, text[:4000], buttons=btns)
        msg_map[m.id] = our_id

@user.on(events.MessageEdited(chats=SEARCH_GROUP))
async def on_edit(event):
    clean_memory()
    m = event.message
    if m.sender_id != SEARCH_ID: return
    if not m.text or not m.buttons: return
    if m.id in msg_map:
        our_id = msg_map[m.id]
        btns = build_buttons(m, our_id)
        text = replace_ads(m.text)
        try: await bot.edit_message(GRUPO, our_id, text[:4000], buttons=btns)
        except: pass

@bot.on(events.NewMessage)
async def on_user_msg(event):
    clean_memory()
    if event.is_private:
        await event.reply("🎬 <b>¡BuddyPelis!</b>\n\n📽️ <b>+5 millones de películas y series</b>\n🔍 Busca sin límites en el grupo\n\n👉 <b>Únete:</b> @BuddyMovies_official", buttons=[[Button.url("🎥 IR AL GRUPO", "https://t.me/BuddyMovies_official")]], link_preview=False)
        return
    if event.out or not event.text: return
    q = event.text.strip()
    if len(q) < 2 or q.startswith("/"): return
    if not check_rate_limit(event.sender_id):
        try: await event.reply("⏳ Espera un momento...")
        except: pass
        return
    try: s = await event.get_sender(); name = s.first_name if s else "Usuario"
    except: name = "Usuario"
    user_sessions[event.sender_id] = {'name': name, 'chat_id': event.chat_id, 'reply_to': event.message.id, 'timestamp': time.time()}
    await user.send_message(SEARCH_GROUP, q)

@bot.on(events.CallbackQuery)
async def on_click(event):
    data = event.data.decode() if isinstance(event.data, bytes) else event.data
    if not data: return
    our_msg_id = event.message_id
    key = (our_msg_id, data)
    if key in button_map:
        info = button_map[key]
        start_param = info[3] if len(info) > 3 else None
        if start_param:
            await event.answer("⚡ Solicitando...")
            await user.send_message(SEARCH_GROUP, f"/start {start_param}")
            return
        try:
            msgs = await user.get_messages(SEARCH_GROUP, ids=[info[0]])
            if msgs and msgs[0].buttons:
                btn = msgs[0].buttons[info[1]][info[2]]
                await event.answer("⚡"); await btn.click(); return
        except: pass
    await event.answer("⏳ Expiró")

async def heartbeat():
    while True:
        await asyncio.sleep(180)
        try: await bot.get_me(); await user.get_me(); clean_memory()
        except: pass

async def main():
    await user.start(); await bot.start(bot_token=BOT_TOKEN)
    print(f"✅ @Angela2_moviebot Bridge → {GRUPO}")
    asyncio.create_task(heartbeat())
    await asyncio.gather(bot.run_until_disconnected(), user.run_until_disconnected())

class H(BaseHTTPRequestHandler):
    def do_GET(self): self.send_response(200); self.end_headers(); self.wfile.write(b"OK")
    def do_HEAD(self): self.send_response(200); self.end_headers()
def run_server(): HTTPServer(("0.0.0.0", int(os.environ.get("PORT", 10000))), H).serve_forever()
threading.Thread(target=run_server, daemon=True).start()

def keep_alive():
    while True:
        time.sleep(600)
        try: urllib.request.urlopen(f"http://localhost:{int(os.environ.get('PORT', 10000))}", timeout=5)
        except: pass
threading.Thread(target=keep_alive, daemon=True).start()

asyncio.run(main())
ENDOFFILE
echo "✅ 5/7"

# Crear bridge_apple.py
cat > ~/mi_bot/bridge_apple.py << 'ENDOFFILE'
import asyncio, re, os, threading, gc, time, urllib.request
from collections import OrderedDict
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from http.server import HTTPServer, BaseHTTPRequestHandler

API_ID = 28074212
API_HASH = "b18dae908474a377684922f3e9d5b795"
BOT_TOKEN = "8760379291:AAHHIOGgqTJT0IINcM4dNV2bOYDXHfV0r7I"
SESSION = "1AZWarzQBu3ZUy3OFCmSneDqRGmhmOequJNsxnU2U1n1U5gCumQo2B_7ve5en_f8KEmXMp7WUE-nWX3SnvxNuBG4xItjnz6L4rYVbZ-OhxEFX8WrF4PdGNXgWWqkgxlH9O7NEZfspmsiRd9QTE9WO0ZRhl-UcY9zXh_066TUxbsInY71vL-0GZjvHHGn1afy9Gj7nphO5h8ockeypg9Kx5bYOJ1bRki36iyrVNbUTpMfFiB4KkEAC1hFlqYoo56EEVEy7piw0TR2L3QDCZnahy3XI8Azpt0JPIc0Y5TZCDUcYyWQtkS5H_CKvnxVTIPitWadXZVHIrQRXz3Lj2KvF6ZyiYUESy0g="
SEARCH_GROUP = "@Apple_moviebot"
SEARCH_ID = 8104769075
CANAL = "@BuddyMovies_canal"
GRUPO = "@BuddyMovies_official"

os.environ['PYTHONOPTIMIZE'] = '2'
gc.set_threshold(5000, 50, 50)
user_sessions = OrderedDict()
button_map = {}
rate_limit = {}
pending_click = None

bot = TelegramClient('apple_bridge', API_ID, API_HASH, retry_delay=3, auto_reconnect=True, timeout=15)
user = TelegramClient(StringSession(SESSION), API_ID, API_HASH, retry_delay=3, auto_reconnect=True, timeout=15)
FOOTER = "\n\n❤️ @BuddyMovies_Bot"

def clean_memory():
    now = time.time()
    expired = [k for k, v in user_sessions.items() if now - v.get('timestamp', 0) > 300]
    for k in expired: user_sessions.pop(k, None)
    if len(button_map) > 2000:
        for k in list(button_map.keys())[:1000]: button_map.pop(k, None)
    gc.collect()

def check_rate_limit(user_id):
    now = time.time()
    if user_id in rate_limit:
        recent = [t for t in rate_limit[user_id] if now - t < 60]
        rate_limit[user_id] = recent
        if len(recent) >= 15: return False
    else: rate_limit[user_id] = []
    rate_limit[user_id].append(now)
    return True

def clean_text(text):
    if not text: return "Sin descripción"
    text = text.replace("Join @F5_FILMS", "").replace("@Apple_Movies101", "")
    text = re.sub(r'https?://\S+', '', text)
    text = text.strip()
    return text if text else "Sin descripción"

def build_buttons(m):
    btns = []
    for row_idx, row in enumerate(m.buttons):
        r = []
        for btn_idx, btn in enumerate(row):
            text = (btn.text or '').strip()
            if btn.url: continue
            if btn.data:
                data = btn.data.decode() if isinstance(btn.data, bytes) else btn.data
                button_map[data] = (m.id, row_idx, btn_idx)
                r.append(Button.inline(text[:50] if text else '📥', data))
        if r: btns.append(r)
    return btns if btns else None

@user.on(events.NewMessage(chats=SEARCH_GROUP))
async def on_result(event):
    global pending_click
    clean_memory()
    m = event.message
    if m.sender_id != SEARCH_ID: return
    
    if pending_click and m.media and not m.photo:
        uid, name, reply_to = pending_click
        pending_click = None
        cap = clean_text(m.text or "") + FOOTER
        sent = await user.send_file(CANAL, m.media, caption=cap)
        link = f"https://t.me/{CANAL[1:]}/{sent.id}"
        await bot.send_message(GRUPO, f"🎬 **{name}**\n\n🔗 {link}", buttons=[[Button.url("🎥 VER CONTENIDO", link)]], reply_to=reply_to)
        return
    
    if not user_sessions: return
    uid = list(user_sessions.keys())[-1]
    s = user_sessions[uid]
    
    if m.photo and m.buttons:
        path = await m.download_media()
        txt = clean_text(m.text)
        btns = build_buttons(m)
        await bot.send_file(GRUPO, path, caption=txt[:1000], buttons=btns, reply_to=s['reply_to'])
        try: os.unlink(path)
        except: pass

@bot.on(events.NewMessage)
async def on_user_msg(event):
    clean_memory()
    if event.is_private:
        await event.reply("🎬 <b>¡BuddyPelis!</b>\n\n📽️ <b>+5 millones de películas y series</b>\n🔍 Busca sin límites en el grupo\n\n👉 <b>Únete:</b> @BuddyMovies_official", buttons=[[Button.url("🎥 IR AL GRUPO", "https://t.me/BuddyMovies_official")]], link_preview=False)
        return
    if event.out or not event.text: return
    q = event.text.strip()
    if len(q) < 2 or q.startswith("/"): return
    if not check_rate_limit(event.sender_id):
        try: await event.reply("⏳ Espera un momento...")
        except: pass
        return
    try: s = await event.get_sender(); name = s.first_name if s else "Usuario"
    except: name = "Usuario"
    user_sessions[event.sender_id] = {'name': name, 'chat_id': event.chat_id, 'reply_to': event.message.id, 'timestamp': time.time()}
    button_map.clear()
    await user.send_message(SEARCH_GROUP, q)

@bot.on(events.CallbackQuery)
async def on_click(event):
    global pending_click
    data = event.data.decode() if isinstance(event.data, bytes) else event.data
    if not data: return
    
    if data in button_map:
        if user_sessions:
            uid = list(user_sessions.keys())[-1]
            s = user_sessions[uid]
            pending_click = (uid, s['name'], s['reply_to'])
        info = button_map[data]
        try:
            msgs = await user.get_messages(SEARCH_GROUP, ids=[info[0]])
            if msgs and msgs[0].buttons:
                btn = msgs[0].buttons[info[1]][info[2]]
                await event.answer("⚡")
                await btn.click()
                return
        except: pass
    await event.answer("⏳ Expiró")

async def heartbeat():
    while True:
        await asyncio.sleep(180)
        try: await bot.get_me(); await user.get_me(); clean_memory()
        except: pass

async def main():
    await user.start(); await bot.start(bot_token=BOT_TOKEN)
    print(f"✅ @Apple_moviebot Bridge → {GRUPO}")
    asyncio.create_task(heartbeat())
    await asyncio.gather(bot.run_until_disconnected(), user.run_until_disconnected())

class H(BaseHTTPRequestHandler):
    def do_GET(self): self.send_response(200); self.end_headers(); self.wfile.write(b"OK")
    def do_HEAD(self): self.send_response(200); self.end_headers()
def run_server(): HTTPServer(("0.0.0.0", int(os.environ.get("PORT", 10000))), H).serve_forever()
threading.Thread(target=run_server, daemon=True).start()

def keep_alive():
    while True:
        time.sleep(600)
        try: urllib.request.urlopen(f"http://localhost:{int(os.environ.get('PORT', 10000))}", timeout=5)
        except: pass
threading.Thread(target=keep_alive, daemon=True).start()

asyncio.run(main())
ENDOFFILE
echo "✅ 6/7"

# Crear bridge_chatgpt.py
cat > ~/mi_bot/bridge_chatgpt.py << 'ENDOFFILE'
import asyncio, re, os, threading, gc, time, urllib.request
from collections import OrderedDict, deque
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from http.server import HTTPServer, BaseHTTPRequestHandler

API_ID = 28074212
API_HASH = "b18dae908474a377684922f3e9d5b795"
BOT_TOKEN = "8952066629:AAHLnoIl62kY0wf4XrFWKiiDq9UaNbjk9zE"
SESSION = "1AZWarzsBu3ny9-HTgWpuIkTxb2vRDvQJu0tU-l_79zEFPRsg1fX4vV7aQw5Qew3KyFIi7-VuZDR3niQvGaXRh89KP2AywppMfdolEwgquZIRROPPNuLQovcl5hpp4vvt6r1gb6Zr1EZrOBOp4PKiG2RLff0b2bKWzRPd-pr5CbDPtTrIBSFMXnMCDwZvs8wxB6n1KZ6H6b5Ndunvr3yOhSKDfzqhWq8Rz3HpGq6iWo1vI418VFHbUXVvlGBe47jEDQc6eaosxAv1EFjRVbmumdQT7aF1GW3u-H_pfpRwpYQHb0r3hVBMCva6eDuTZ_L5rOaE2Zix41Z3C51umX6FZjdHGuyed20="
CHATBOT = "@gpt3ru_chat_bot"
CHATBOT_ID = 6157862059
GRUPO = "@BuddyMovies_official"

os.environ['PYTHONOPTIMIZE'] = '2'
gc.set_threshold(5000, 50, 50)
question_queue = deque()
rate_limit = {}

bot = TelegramClient('chatgpt_final', API_ID, API_HASH, retry_delay=3, auto_reconnect=True, timeout=15)
user = TelegramClient(StringSession(SESSION), API_ID, API_HASH, retry_delay=3, auto_reconnect=True, timeout=15)

def clean_memory():
    if len(question_queue) > 100:
        for _ in range(50): question_queue.popleft()
    gc.collect()

def check_rate_limit(user_id):
    now = time.time()
    if user_id in rate_limit:
        recent = [t for t in rate_limit[user_id] if now - t < 60]
        rate_limit[user_id] = recent
        if len(recent) >= 10: return False
    else: rate_limit[user_id] = []
    rate_limit[user_id].append(now)
    return True

def clean_response(text):
    text = re.sub(r'https?://\S+', '', text)
    return text.strip()

@user.on(events.NewMessage(chats=CHATBOT))
async def on_response(event):
    clean_memory()
    m = event.message
    if m.sender_id != CHATBOT_ID: return
    if m.text and "please wait" in m.text.lower(): return
    
    if question_queue and m.text:
        uid, name, reply_to = question_queue.popleft()
        clean = clean_response(m.text)
        try:
            await bot.send_message(GRUPO, f"🤖 **GPT para {name}:**\n\n{clean[:2000]}", reply_to=reply_to)
        except:
            await bot.send_message(GRUPO, f"🤖 **GPT para {name}:**\n\n{clean[:2000]}")

@bot.on(events.NewMessage)
async def on_user_msg(event):
    clean_memory()
    if event.is_private:
        await event.reply("🤖 <b>ChatGPT Bot</b>\n\n💬 Haz tus preguntas en el grupo\n\n👉 <b>Únete:</b> @BuddyMovies_official", buttons=[[Button.url("🎥 IR AL GRUPO", "https://t.me/BuddyMovies_official")]], link_preview=False)
        return
    if event.out or not event.text: return
    q = event.text.strip()
    if len(q) < 2 or q.startswith("/"): return
    if not check_rate_limit(event.sender_id):
        try: await event.reply("⏳ Espera un momento...")
        except: pass
        return
    try: s = await event.get_sender(); name = s.first_name if s else "Usuario"
    except: name = "Usuario"
    question_queue.append((event.sender_id, name, event.message.id))
    await user.send_message(CHATBOT, q)

async def heartbeat():
    while True:
        await asyncio.sleep(180)
        try: await bot.get_me(); await user.get_me(); clean_memory()
        except: pass

async def main():
    await user.start(); await bot.start(bot_token=BOT_TOKEN)
    print(f"✅ ChatGPT Bridge → {GRUPO}")
    asyncio.create_task(heartbeat())
    await asyncio.gather(bot.run_until_disconnected(), user.run_until_disconnected())

class H(BaseHTTPRequestHandler):
    def do_GET(self): self.send_response(200); self.end_headers(); self.wfile.write(b"OK")
    def do_HEAD(self): self.send_response(200); self.end_headers()
def run_server(): HTTPServer(("0.0.0.0", int(os.environ.get("PORT", 10000))), H).serve_forever()
threading.Thread(target=run_server, daemon=True).start()

def keep_alive():
    while True:
        time.sleep(600)
        try: urllib.request.urlopen(f"http://localhost:{int(os.environ.get('PORT', 10000))}", timeout=5)
        except: pass
threading.Thread(target=keep_alive, daemon=True).start()

asyncio.run(main())
ENDOFFILE
echo "✅ 7/7"

echo ""
echo "🎉 ARCHIVOS CREADOS. INICIANDO BRIDGES..."
echo ""

# Matar anteriores
pkill -f "python ~/mi_bot/bridge_" 2>/dev/null
sleep 1

# Iniciar
cd ~/mi_bot
nohup python bridge_simple.py > logs/simple.log 2>&1 &
echo "✅ 1/7 @BuddyMovies_Bot (PID: $!)"
nohup python bridge_searchbot.py > logs/searchbot.log 2>&1 &
echo "✅ 2/7 @BuddyNotify_Bot (PID: $!)"
nohup python bridge_autofilter.py > logs/autofilter.log 2>&1 &
echo "✅ 3/7 @AutoFilter (PID: $!)"
nohup python bridge_ltmovie.py > logs/ltmovie.log 2>&1 &
echo "✅ 4/7 @Lt_Moviebot (PID: $!)"
nohup python bridge_angela.py > logs/angela.log 2>&1 &
echo "✅ 5/7 @Angela2 (PID: $!)"
nohup python bridge_apple.py > logs/apple.log 2>&1 &
echo "✅ 6/7 @Apple (PID: $!)"
nohup python bridge_chatgpt.py > logs/chatgpt.log 2>&1 &
echo "✅ 7/7 ChatGPT (PID: $!)"

echo ""
echo "========================================="
echo "  🎉 ¡7 BRIDGES INICIADOS!"
echo "========================================="
