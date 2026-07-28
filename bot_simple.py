import asyncio, re, os, json, time
from collections import OrderedDict
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession

API_ID = 28074212
API_HASH = "b18dae908474a377684922f3e9d5b795"
BOT_TOKEN = "8724266934:AAEEzhSF2s6ZE8aR2zAHeJeGDzuhQWRCNdc"
SESSION = "1AZWarzQBu5hWbHakw_V4c82HJA0uCNxvwdS_2JHHEVUbCghWQtCFrCbvfFEAMYTh1sCL3mMpTCJMmETKHXkmgBhynikL_1MTEXJfDlFxjnZQDXf1Glbd5w0HuyCQwEP6K_F2DnAS5vsGtH452l_HDS0uQMAGryhoTV7n5Tr9-5E1DmwY4CfKNV7uzYat15FQ6Nsm_vu8iPnQEwy5w5egiY_xnULhFKIkjWrr9gm7WS_OZbSwmEThy32o3I7zxIO__BiRmAFqPnICFo8OJR_FqU7JYoGvHeScnbgbOGU-bcmFUZrq_sFBbldOn1Y4G0TBw6gLeCCUjhwIh-td7KAjaDIRdaoI_lc="
SEARCH = "@pooppuuui"

def clean(text):
    if not text: return ""
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\n\n\n+', '\n\n', text)
    return text.strip()
CANAL = "@BuddyMovies_canal"
GRUPO = "@BuddyMovies_official"

sessions = OrderedDict()
bot = TelegramClient('bs', API_ID, API_HASH, retry_delay=5, auto_reconnect=True, timeout=10)
user = TelegramClient(StringSession(SESSION), API_ID, API_HASH, retry_delay=5, auto_reconnect=True, timeout=10)

@user.on(events.NewMessage(chats=SEARCH))
async def on_res(event):
    m = event.message
    if not m.sender or not m.sender.bot: return
    if m.media and sessions:
        uid = list(sessions.keys())[-1]
        s = sessions[uid]
        raw = clean(m.text) + "\n\n📌 @BuddyMovies_Bot"
        sent = await user.send_file(CANAL, m.media, caption=raw)
        link = f"https://t.me/{CANAL[1:]}/{sent.id}"
        await bot.send_message(GRUPO, f"🎬 {link}", buttons=[[Button.url("VER", link)]], reply_to=s.get('reply_to'))
    elif m.text and m.buttons:
        for uid, s in list(sessions.items()):
            try: await bot.send_message(s['chat_id'], m.text[:4000], buttons=m.buttons, reply_to=s.get('reply_to'))
            except: pass
            break

@bot.on(events.NewMessage)
async def on_msg(event):
    if event.is_private or event.out or not event.text: return
    q = event.text.strip()
    if len(q) < 2 or q.startswith("/"): return
    try:
        if os.path.exists('pendientes.json'):
            if str(event.sender_id) in json.load(open('pendientes.json')): return
    except: pass
    sessions[event.sender_id] = {'chat_id': event.chat_id, 'reply_to': event.message.id}
    await user.send_message(SEARCH, f"/search {q}")

async def main():
    await user.start()
    await bot.start(bot_token=BOT_TOKEN)
    print("✅ Simple")
    await asyncio.gather(bot.run_until_disconnected(), user.run_until_disconnected())
asyncio.run(main())
