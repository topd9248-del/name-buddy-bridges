import asyncio, re, os, json, time
from collections import OrderedDict
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession

API_ID = 28074212
API_HASH = "b18dae908474a377684922f3e9d5b795"
BOT_TOKEN = "8463069047:AAFw2frWMhqfELqxQzgplSODDC1kRuCJyII"
SESSION = "1AZWarzQBuzncKy_mbzKcjlq0_XeKVuhMaiHWMBs3kkt9hmss9EcHTh9f9RtgQYkoDx4oXfLs8rnlwzNA8AHxmt47X2J3r4YJr0QVNVzX3meQKnDv1EKsnctVofcPlsHGuXPZutTrhs0-rtMFXO8TYMESuLbcu0BlENZDA6LVWzItTe17yMvgWexGLJMIyhO-yIrRxHr4838YkKxdxUflsSkjtSZIV8W4EWtrd6eOcTcZbaQyJEUT6jcyXrePbmfaOjMoOsx1PJF1dQisoPP_C-mRSHgp59Za4LmBM4EqQgzXeoPdUdXFRDkCJAfjzc3p6lnU7HqEtcKmm2EIzY43vj_iKSroOOo="
SEARCH = "@TlgramMovieSearch_Bot"
CANAL = "@BuddyMovies_canal"
GRUPO = "@BuddyMovies_official"

sessions = OrderedDict()
sr = {}
bm = {}
bot = TelegramClient('br', API_ID, API_HASH, retry_delay=5, auto_reconnect=True, timeout=10)
user = TelegramClient(StringSession(SESSION), API_ID, API_HASH, retry_delay=5, auto_reconnect=True, timeout=10)

@user.on(events.NewMessage(chats=SEARCH))
async def on_res(event):
    m = event.message
    if not m.sender or not m.sender.bot: return
    
    if m.text and "selecciona un método" in m.text.lower():
        if m.buttons and m.buttons[0]: await m.buttons[0][0].click(); return
    if m.text and "selecciona un almacén" in m.text.lower():
        if m.buttons and m.buttons[0]: await m.buttons[0][0].click(); return
    
    if m.media and sessions:
        uid = list(sessions.keys())[-1]
        s = sessions[uid]
        raw = m.text or ""
        sent = await user.send_file(CANAL, m.media, caption=raw)
        link = f"https://t.me/{CANAL[1:]}/{sent.id}"
        await bot.send_message(GRUPO, f"🎬 {link}", buttons=[[Button.url("VER", link)]], reply_to=s.get('reply_to'))
    elif m.text and m.buttons:
        for uid, s in list(sessions.items()):
            try:
                sent = await bot.send_message(s['chat_id'], m.text[:4000], buttons=m.buttons, reply_to=s.get('reply_to'))
                if sent: sr[m.id] = (s['chat_id'], sent.id)
            except: pass
            break

@user.on(events.MessageEdited(chats=SEARCH))
async def on_edit(event):
    m = event.message
    if m.text and m.buttons and m.id in sr:
        try: await bot.edit_message(sr[m.id][0], sr[m.id][1], m.text[:4000], buttons=m.buttons)
        except: pass

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
    await user.send_message(SEARCH, q)

async def main():
    await user.start()
    await bot.start(bot_token=BOT_TOKEN)
    print("✅ Search")
    await asyncio.gather(bot.run_until_disconnected(), user.run_until_disconnected())
asyncio.run(main())
