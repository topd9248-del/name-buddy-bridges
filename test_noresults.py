import asyncio, re, time
from collections import OrderedDict
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession

API_ID = 28074212
API_HASH = "b18dae908474a377684922f3e9d5b795"
BOT_TOKEN = "8724266934:AAFZQQwhJvfkebr1csgnIKwMZKkXa44eGyA"
SESSION_READER = "1AZWarzgBu13W0EuNpoxKErbi-sroDDYq6ZWDiIaNcoKjzWrZ5J5uXknAAh-Pq7cgtT-GrhwS5rcoWmzXj5B1EsOIQsFR5qxzoJLAXUPvtEOd8eaV4BsSXyF3G8jRAPqGmbjx7FjepBwg6_TYIDUqeA6CSrkhlSIkNZ-YhTyScCvUoT_0gIQazF4KCC7jsFo1FMxQEPPgJJ3WB0QgRoHqojHEAeJ6MVxcTFmucaQKfjTkrBIlTiQdlHAJzwq7jvOd9c10TUurK0YWPgxfcCE_orEcz_CMhURbK7gJ1kSKHFx-jf3a6MGhzWclKLOkuuizGmOSJnzEkgmfIntIE_Ig3qr2qcbFgno="

SEARCH_GROUP = "@pooppuuui"
GRUPO = "@mabu205"
BOT_ID = 7537528826

user_sessions = {}
last_search = {}

bot = TelegramClient('test_nores', API_ID, API_HASH)
reader = TelegramClient(StringSession(SESSION_READER), API_ID, API_HASH)

@reader.on(events.NewMessage(chats=SEARCH_GROUP))
async def on_new(event):
    m = event.message
    if m.sender_id != BOT_ID: return
    if m.text: print(f"🆕 '{m.text[:200]}'")

@reader.on(events.MessageEdited(chats=SEARCH_GROUP))
async def on_edit(event):
    m = event.message
    if m.sender_id != BOT_ID: return
    if m.text:
        print(f"✏️ '{m.text[:300]}'")
        txt = m.text.lower()
        if any(x in txt for x in ['no results', 'not found', 'not available', 'no se encontro', 'sin resultados']):
            print("   ⚠️ DETECTADO 'NO ENCONTRADO'")
            if user_sessions:
                uid = list(user_sessions.keys())[-1]
                s = user_sessions[uid]
                q = last_search.get(uid, "tu búsqueda")
                await bot.send_message(GRUPO,
                    f"🚫 No encontramos resultados para {q}.\n"
                    f"🔍 Por favor, revisa la ortografía o intenta con una variación diferente.",
                    reply_to=s['rid'])
                print(f"   📤 Mensaje enviado")

@bot.on(events.NewMessage)
async def on_user(event):
    if event.out or not event.text: return
    q = event.text.strip()
    if len(q) < 2: return
    try: name = (await event.get_sender()).first_name or "Usuario"
    except: name = "Usuario"
    uid = event.sender_id
    user_sessions[uid] = {'name': name, 'rid': event.message.id, 't': time.time()}
    last_search[uid] = q
    await reader.send_message(SEARCH_GROUP, f"/search {q}")
    print(f"📤 {name}: {q}")

async def main():
    await reader.start()
    await bot.start(bot_token=BOT_TOKEN)
    print("✅ Conectado - Busca algo que no exista en @mabu205\n")
    await asyncio.sleep(300)
    await bot.disconnect()
    await reader.disconnect()

asyncio.run(main())
