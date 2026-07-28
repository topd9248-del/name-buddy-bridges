import asyncio, re, os, gc, time
from collections import OrderedDict
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession

API_ID = 28074212
API_HASH = "b18dae908474a377684922f3e9d5b795"
BOT_TOKEN = "8724266934:AAEEzhSF2s6ZE8aR2zAHeJeGDzuhQWRCNdc"
SESSION = "1AZWarzQBu5hWbHakw_V4c82HJA0uCNxvwdS_2JHHEVUbCghWQtCFrCbvfFEAMYTh1sCL3mMpTCJMmETKHXkmgBhynikL_1MTEXJfDlFxjnZQDXf1Glbd5w0HuyCQwEP6K_F2DnAS5vsGtH452l_HDS0uQMAGryhoTV7n5Tr9-5E1DmwY4CfKNV7uzYat15FQ6Nsm_vu8iPnQEwy5w5egiY_xnULhFKIkjWrr9gm7WS_OZbSwmEThy32o3I7zxIO__BiRmAFqPnICFo8OJR_FqU7JYoGvHeScnbgbOGU-bcmFUZrq_sFBbldOn1Y4G0TBw6gLeCCUjhwIh-td7KAjaDIRdaoI_lc="
SEARCH_GROUP = "@pooppuuui"
CANAL = "@BuddyMovies_canal"
GRUPO = "@BuddyMovies_official"

user_sessions = OrderedDict()
search_results = {}
button_map = {}
rate_limit = {}

bot = TelegramClient('b1', API_ID, API_HASH, retry_delay=3, auto_reconnect=True, timeout=10)
user = TelegramClient(StringSession(SESSION), API_ID, API_HASH, retry_delay=3, auto_reconnect=True, timeout=10)

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
    return text.replace("@TlgramMovieGroup_Bot", "@BuddyMovies_Bot").replace("@FILM_PARADIZE", "@BuddyMovies_official")

@user.on(events.NewMessage(chats=SEARCH_GROUP))
async def on_result(event):
    m = event.message
    if not m.sender or not m.sender.bot: return
    if m.media and user_sessions:
        uid = list(user_sessions.keys())[-1]
        session = user_sessions[uid]
        raw = replace_ads(m.text or "")
        sent = await user.send_file(CANAL, m.media, caption=raw)
        link = f"https://t.me/{CANAL[1:]}/{sent.id}"
        await bot.send_message(GRUPO, f"🎬 {link}", buttons=[[Button.url("VER", link)]], reply_to=session.get('reply_to'))
    elif m.text and m.buttons and len(m.text) > 20:
        text = replace_ads(m.text)
        for uid, session in list(user_sessions.items()):
            try:
                sent = await bot.send_message(session.get('chat_id', GRUPO), text[:4000], buttons=m.buttons, reply_to=session.get('reply_to'))
                if sent: search_results[m.id] = (session.get('chat_id', GRUPO), sent.id)
            except: pass
            break

@user.on(events.MessageEdited(chats=SEARCH_GROUP))
async def on_edit(event):
    m = event.message
    if not m.sender or not m.sender.bot or not m.text: return
    if m.text and m.buttons and m.id in search_results:
        try: await bot.edit_message(search_results[m.id][0], search_results[m.id][1], m.text[:4000], buttons=m.buttons)
        except: pass

@bot.on(events.NewMessage)
async def on_user_msg(event):
    if event.is_private: return
    if event.out or not event.text: return
    q = event.text.strip()
    if len(q) < 2 or q.startswith("/"): return
    if not check_rate_limit(event.sender_id): return
    try:
        import json
        if os.path.exists('pendientes.json'):
            with open('pendientes.json') as f:
                if str(event.sender_id) in json.load(f): return
    except: pass
    name = (await bot.get_entity(event.sender_id)).first_name or "Usuario"
    user_sessions[event.sender_id] = {'name': name, 'chat_id': event.chat_id, 'reply_to': event.message.id, 'timestamp': time.time()}
    await user.send_message(SEARCH_GROUP, f"/search {q}")

@bot.on(events.CallbackQuery)
async def on_click(event):
    data = event.data.decode() if isinstance(event.data, bytes) else event.data
    if data in button_map:
        try:
            msgs = await user.get_messages(SEARCH_GROUP, ids=[button_map[data][0]])
            if msgs and msgs[0].buttons:
                await event.answer("⚡")
                await msgs[0].buttons[button_map[data][1]][button_map[data][2]].click()
                return
        except: pass

async def main():
    await user.start()
    await bot.start(bot_token=BOT_TOKEN)
    await asyncio.gather(bot.run_until_disconnected(), user.run_until_disconnected())

asyncio.run(main())
