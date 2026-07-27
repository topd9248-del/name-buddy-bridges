import asyncio, re, os, gc, time
from collections import OrderedDict
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession

API_ID = 28074212
API_HASH = "b18dae908474a377684922f3e9d5b795"
BOT_TOKEN = "8463069047:AAFw2frWMhqfELqxQzgplSODDC1kRuCJyII"
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

def cache_buttons(msg):
    if not msg or not msg.buttons: return None
    for row in msg.buttons:
        for btn in row:
            if btn.data:
                data = btn.data.decode() if isinstance(btn.data, bytes) else btn.data
                button_map[data] = (msg.id, msg.buttons.index(row), row.index(btn))
    return msg.buttons

def clean_memory():
    now = time.time()
    expired = [k for k, v in user_sessions.items() if now - v.get('timestamp', 0) > 300]
    for k in expired: user_sessions.pop(k, None)
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
    text = text.replace("@TlgramMovieSearch_Bot", "@BuddyNotify_Bot")
    text = text.replace("@TlgramMovieGroup_Bot", "@BuddyMovies_Bot")
    text = re.sub(r'https?://\S*terabox\S*', '', text)
    return text

@user.on(events.NewMessage(chats=SEARCH_GROUP))
async def on_result(event):
    clean_memory()
    m = event.message
    if not m.sender or not m.sender.bot: return
    
    # AUTO-CLICK 1: metodo
    if m.text and "selecciona un método" in m.text.lower():
        if m.buttons and m.buttons[0] and m.buttons[0][0]:
            await asyncio.sleep(0.3)
            await m.buttons[0][0].click()
            return
    
    # AUTO-CLICK 2: almacen
    if m.text and "selecciona un almacén" in m.text.lower():
        if m.buttons and m.buttons[0] and m.buttons[0][0]:
            await asyncio.sleep(0.3)
            await m.buttons[0][0].click()
            return
    
    if m.text and any(x in m.text.lower() for x in ["procesando", "espera", "maldito", "comparte"]): return
    
    # SI LLEGA MEDIA -> ENVIAR AL CANAL
    if m.media:
        print(f"📤 VIDEO DETECTADO - Enviando al canal...", flush=True)
        if user_sessions:
            uid = list(user_sessions.keys())[-1]
            session = user_sessions[uid]
            name = session.get('name', 'Usuario')
            reply_to = session.get('reply_to')
        else:
            name = "Usuario"
            reply_to = None
        raw = replace_ads(m.text or "")
        try:
            sent = await user.send_file(CANAL, m.media, caption=raw)
            link = f"https://t.me/{CANAL[1:]}/{sent.id}"
            title = raw.split('\n')[0][:80] if raw else "Archivo"
            await bot.send_message(GRUPO, f"🎬 **{name}**\n📁 {title}\n\n🔗 {link}", buttons=[[Button.url("🎥 VER CONTENIDO", link)]], link_preview=False, reply_to=reply_to)
            print(f"✅ Enviado: {link}", flush=True)
        except Exception as e:
            print(f"❌ Error: {e}", flush=True)
        return
    
    # Si es texto con botones
    if m.text and m.buttons and len(m.text) > 20:
        if 'no se encontraron' in m.text.lower(): return
        text = replace_ads(m.text)
        cache_buttons(m)
        for uid, session in list(user_sessions.items()):
            try:
                await bot.send_message(session.get('chat_id', GRUPO), text[:4000], buttons=m.buttons, reply_to=session.get('reply_to'))
            except: pass
            break

@user.on(events.MessageEdited(chats=SEARCH_GROUP))
async def on_edit(event):
    m = event.message
    if not m.sender or not m.sender.bot or not m.text: return
    if m.text and m.buttons and len(m.text) > 20:
        if 'no se encontraron' in m.text.lower(): return
        text = replace_ads(m.text)
        cache_buttons(m)
        for uid, session in list(user_sessions.items()):
            try:
                await bot.send_message(session.get('chat_id', GRUPO), text[:4000], buttons=m.buttons, reply_to=session.get('reply_to'))
            except: pass
            break

@bot.on(events.NewMessage)
async def on_user_msg(event):
    clean_memory()
    if event.is_private:
        await event.reply("🎬 ¡BuddyPelis!\n👉 @BuddyMovies_official", buttons=[[Button.url("IR AL GRUPO", "https://t.me/BuddyMovies_official")]], link_preview=False)
        return
    if event.out or not event.text: return
    q = event.text.strip()
    if len(q) < 2 or q.startswith("/"): return
    if not check_rate_limit(event.sender_id):
        try: await event.reply("⏳ Espera...")
        except: pass
        return
    try: sender = await bot.get_entity(event.sender_id); name = sender.first_name or "Usuario"
    except: name = "Usuario"
    user_sessions[event.sender_id] = {'name': name, 'chat_id': event.chat_id, 'reply_to': event.message.id, 'timestamp': time.time()}
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
    await event.answer("⏳ Expiró")

async def heartbeat():
    while True:
        await asyncio.sleep(180)
        try: await bot.get_me(); await user.get_me(); clean_memory()
        except: pass

async def main():
    await user.start(); await bot.start(bot_token=BOT_TOKEN)
    print(f"✅ @BuddyNotify_Bot → {GRUPO}", flush=True)
    asyncio.create_task(heartbeat())
    await asyncio.gather(bot.run_until_disconnected(), user.run_until_disconnected())

asyncio.run(main())
