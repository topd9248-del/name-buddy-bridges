import asyncio, os, time, threading, urllib.request
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from telethon.tl.types import ChatAdminRights
from http.server import HTTPServer, BaseHTTPRequestHandler

API_ID = 28074212
API_HASH = "b18dae908474a377684922f3e9d5b795"
BOT_TOKEN = "8964309642:AAHgJSUvT4yxg9RB02Z0Ve6tG6EmSQzBlBg"
SESSIONS = [
    "1AZWarzsBu4STAQEQjoPhdDEN4XfnBqKQzWmgw8F8nUVt6TQx8101RCp0oxrhwcg1x4sq7rjlV2xWVl6ScaQrv2jXU8DyRjTfPIFeYEQpRVncpEdEbwcliu_NAiMzpgxZd4fPNoCcQ1i4-EmQqBdQPYX90VokgQaO-G6iKP8zuSGzm4AChajII3Ush6K8Z27uJQGl7dr4gCLWV7IsgEkUtXeNT8Yz8sMdBW9whSQBZn3btCTsWHI1XUY3PztsbIyFczAgYvROlyOGzVVueiqztB1SDqMNcojcWRbpL08tmqQb45jp00wflFX6UM_hfG1kJIB6q3dYuwbbo0_oxfItzqYs_OsTyrc=",
    "1AZWarzQBu4RpYUafm-K64e2G0lF5WWBiweaeiwIxCtz_lUlpxVpEul31rxKYrl1iM7Qy8Lm_IwHzVYMH8v9V2miRODgQ1MpdRd0FVFk71E3Ft5JQfH0dmePYe6i2JbFE5OyJK3DzwOIN0INJrzuc_7_KAuBVEg5rMbFwLoqFNiWLAKqQYjVOpPcnE5L4iZ3-a9pOSCmDmnHSKxxDpGJ4nXjWDAahpmOGreOYBfMl9y3z0Ok_NTBb9sOeRiBGDzixXwIOa0-5sbjDj0Xvy2w4HAxsBj6da9NFOVBu5mPZ69TEPotoZXofZPBDtpj85txK7O-KObnQvBwh1WzOBXjLSiDVpZbzed4=",
    "1AZWarzkBu2YBGExnst_V3sZheBKHyC6Vf1wWslQ-zxnZEN_TB-KxzYII7McBJVl3oNFQUaBkcfiFiqwy5vC5EiPvfGRsJUevjZpC0-fr-JZ3RyAGe7U7UZHowjh0jHheV826KHdyWQ2QZoJvIyT0gm4No3M6kxaO-WGd-Pb1s-jmrnx1k_MlvXXHAmTsQBSJmeegB7nLrZW22BA9ToHaaQxYd1xN082CCGyNlATs-319BwGsSz7ct0lg1vnu8YDpp-3Jef0xG4e7AMALoK5mSJKJktTq1i1D8lNi_AzJGElanlHtb_XilXraTo_vhNSWOJGgAY7EFANVg1Ku8N9_vKtwAxeX0Hs=",
    "1AZWarzwBuxlEgUc6dMYfh3uBFpBiu00ZO0-vCLTQYGf7XLzamqeMZFSEzRStGEhaWplflnOU02Unj_0rGHKp3wgydHIJ9sY7ogTcFDwrZdUCVA4Gs7BV7c9sNab_surgCri0dvV-0yBqU9Q_3llifikSYK6YWEj15W-4WwXcj9n-z7vpKUFaeWPYYne0TOENFyzZjR7ajqwo-w-XDoS6i2Gj2FH7WGZBoy515tGpDT_eKWg8_OkvnN4jqwhEYkDqNgs2nGR6kWpkFrlO6kS3IjTuRDYFfWBhqsM6sbvnwKX9TOObEee_LkMiQ0rS7xoKWhZYPftQNyy5pH1cYh8xBRZA_hae6tM=",
    "1AZWarzUBu5AYxpP4Akh2KMHOHTLr2yLXG0K4t2zltoZmwVXFPcthQvD2pTIrHHteELie10Sbs__2CwWXaMcDS0tto4wZUhDQpHnHs5__MUY8l9DRhWgrw6hjCQ2lsXNwRH8tMwMh3-XDJYeK0Q924pe7b9NWki6D6PdfaprX_spu4s0LuFn_BxzXUht5Ny6BqurftEwxxRSatLt-GF7j5jNzTP-OzQXFKnGLV40I6oPOGockqO7collR_1OtxFCdWomH_Gb3UwNXij4_pGKQNcsTpuX28nwAl9Gy9WN0oTzl9RelN4_0f8-br2R_I-lx5uHvPtDAIZ5WkrsQ3cVPPaIE4edKk-w="
]
CLONE_BOT = "@Buddy_musicbot"
CLONE_ID = 1584661938
CANAL = "@Descarga_Musica_clic"
GRUPO = -1004388150705
FOOTER = "\n\n🎧 [Disfruta tu música 🎵](https://t.me/+ZlZMjjKP5GsxZTQ5)"
SKIP_BUTTONS = ['« Меню', 'Глубокий поиск', '🔍 Búsqueda profunda', '« Menu', 'Deep search', '🔍 Deep search']

search_map = {}
client_to_search = {}
button_to_search = {}
session_idx = 0
sessions_pool = []
search_lock = asyncio.Lock()

async def init_sessions():
    for sess in SESSIONS:
        c = TelegramClient(StringSession(sess), API_ID, API_HASH, retry_delay=5, auto_reconnect=True, timeout=15)
        await c.start()
        sessions_pool.append(c)
    print(f"✅ {len(sessions_pool)} sesiones listas")

def next_session():
    global session_idx
    c = sessions_pool[session_idx % len(sessions_pool)]
    session_idx += 1
    return c

bot = TelegramClient('music_v19', API_ID, API_HASH, retry_delay=5, auto_reconnect=True, timeout=15)

def filtrar_botones(buttons):
    if not buttons: return None
    fb = []
    for row in buttons:
        r = []
        for btn in row:
            texto = btn.text or ''
            if any(s.lower() in texto.lower() for s in SKIP_BUTTONS): continue
            if texto.strip() in ['🔍', '🔎', '«', '»']: continue
            r.append(btn)
        if r: fb.append(r)
    return fb if fb else None

def register_buttons_for_search(msg_id_grupo, buttons):
    if not buttons or msg_id_grupo not in search_map: return
    if 'buttons_map' in search_map[msg_id_grupo]:
        for old_data in search_map[msg_id_grupo]['buttons_map']:
            button_to_search.pop(old_data, None)
    search_map[msg_id_grupo]['buttons_map'] = {}
    for row in buttons:
        for btn in row:
            if btn.data:
                bd = btn.data.decode() if isinstance(btn.data, bytes) else btn.data
                button_to_search[bd] = msg_id_grupo
                search_map[msg_id_grupo]['buttons_map'][bd] = True

async def setup_handler(client):
    @client.on(events.NewMessage(chats=[CLONE_BOT]))
    async def on_music(event):
        m = event.message
        if not m.sender or not m.sender.bot: return
        if m.media:
            async with search_lock:
                search_id = client_to_search.get(id(client))
                if not search_id or search_id not in search_map:
                    for gid, info in list(search_map.items()):
                        if info['client'] == client:
                            search_id = gid
                            client_to_search[id(client)] = gid
                            break
                    else: return
                info = search_map[search_id]
                cap = f"🎵 Canción de {info['query']}{FOOTER}"
                try:
                    await client.send_file(GRUPO, m.media, caption=cap, reply_to=info['reply_id'])
                except: pass
                return

    @client.on(events.MessageEdited)
    async def on_edit(event):
        m = event.message
        if not m.text or not m.buttons: return
        chat = await event.get_chat()
        if getattr(chat, 'id', 0) != CLONE_ID: return
        if "Нажми" in m.text: return
        async with search_lock:
            search_id = client_to_search.get(id(client))
            if not search_id or search_id not in search_map: return
            info = search_map[search_id]
            if info.get('clone_msg_id') == m.id:
                try:
                    fb = filtrar_botones(m.buttons)
                    if fb:
                        await bot.edit_message(GRUPO, search_id, m.text, buttons=fb)
                    else:
                        await bot.edit_message(GRUPO, search_id, m.text)
                    register_buttons_for_search(search_id, m.buttons)
                    info['timestamp'] = time.time()
                except: pass

    @client.on(events.NewMessage)
    async def on_buttons(event):
        m = event.message
        if not m.text or not m.buttons: return
        chat = await event.get_chat()
        if getattr(chat, 'id', 0) != CLONE_ID: return
        if "Нажми" in m.text: return
        async with search_lock:
            search_id = client_to_search.get(id(client))
            if not search_id or search_id not in search_map: return
            info = search_map[search_id]
            if info.get('clone_msg_id') is None:
                fb = filtrar_botones(m.buttons)
                try:
                    if fb:
                        await bot.edit_message(GRUPO, search_id, m.text, buttons=fb)
                    else:
                        await bot.edit_message(GRUPO, search_id, m.text)
                except:
                    sent = await bot.send_message(GRUPO, m.text, buttons=fb if fb else None, reply_to=info.get('reply_id'))
                    old_gid = search_id
                    search_map[sent.id] = search_map.pop(old_gid)
                    client_to_search[id(client)] = sent.id
                    search_id = sent.id
                info = search_map[search_id]
                info['clone_msg_id'] = m.id
                info['timestamp'] = time.time()
                register_buttons_for_search(search_id, m.buttons)

async def es_admin_o_bot(event):
    sender = await event.get_sender()
    if sender.bot: return True
    try:
        perms = await event.client.get_permissions(event.chat_id, sender.id)
        if perms.is_admin: return True
    except: pass
    return False

@bot.on(events.NewMessage)
async def on_user(event):
    if event.out: return
    if await es_admin_o_bot(event): return
    text = event.message.text or ""
    if any(kw in text.lower() for kw in ['@', '+18', '18+', '.com', '.net', '.org', '.site', '.xyz', 'amateur', 'apuestas', 'bdsm', 'bit.ly', 'bot', 'buddy_musicbot', 'canal', 'coger', 'coño', 'culo', 'desnuda', 'desnudo', 'desnudos', 'discord.gg', 'enlace', 'erótica', 'erótico', 'explícita', 'explícito', 'fetish', 'fetiche', 'follar', '🖕', 'gana dinero rápido', 'ganar', 'gore', 'gratis', 'grupo', 'hentai', 'http', 'http://', 'https://', 'https://wa.me/', 'incesto', 'link', 'mamar', 'masturbar', 'masturbación', 'nopor', 'orgasmo', 'orgía', 'p0rno', 'paja', 'pederasta', 'pedofilia', 'pene', 'pija', 'polla', 'porno', 'pornografía', 'premio', 'puta', 'putas', 'puto', 'putos', 'rule34', 's3x', 's3xo', 'sado', 'sadismo', 'senos', 'sexo', 't.me/', 'telegram.me/', 'teta', 'tetas', 'tinyurl', 'trasero', 'unete', 'unirse', 'url', 'únete', 'vagina', 'verga', 'violar', 'violación', 'xxx']):
        try: await event.delete()
        except: pass
        return
    client = next_session()
    sent = await event.reply("🔍 Buscando...")
    async with search_lock:
        search_map[sent.id] = {
            'client': client,
            'clone_msg_id': None,
            'query': event.message.text,
            'reply_id': event.message.id,
            'songs_sent': 0,
            'buttons_map': {},
            'timestamp': time.time()
        }
        client_to_search[id(client)] = sent.id
    await client.send_message(CLONE_BOT, event.message.text)

@bot.on(events.CallbackQuery)
async def on_click(event):
    data = event.data.decode() if isinstance(event.data, bytes) else event.data
    msg_id = event.message_id
    async with search_lock:
        if msg_id not in search_map:
            fallback_id = button_to_search.get(data)
            if fallback_id and fallback_id in search_map:
                msg_id = fallback_id
            else:
                await event.answer("🔎 Realiza una nueva búsqueda.")
                return
        info = search_map[msg_id]
        if data not in info.get('buttons_map', {}):
            await event.answer("🔎 Realiza una nueva búsqueda.")
            return
        client = info['client']
        info['timestamp'] = time.time()
        try:
            if info.get('clone_msg_id'):
                msgs = await client.get_messages(CLONE_BOT, ids=[info['clone_msg_id']])
                if msgs and msgs[0].buttons:
                    for row in msgs[0].buttons:
                        for btn in row:
                            if btn.data:
                                bd = btn.data.decode() if isinstance(btn.data, bytes) else btn.data
                                if bd == data:
                                    await event.answer("⚡ Procesando...")
                                    await btn.click()
                                    return
            async for m in client.iter_messages(CLONE_BOT, limit=10):
                if m.buttons:
                    for row in m.buttons:
                        for btn in row:
                            if btn.data:
                                bd = btn.data.decode() if isinstance(btn.data, bytes) else btn.data
                                if bd == data:
                                    search_map[msg_id]['clone_msg_id'] = m.id
                                    await event.answer("⚡ Procesando...")
                                    await btn.click()
                                    return
        except: pass
    await event.answer("🔎 Realiza una nueva búsqueda.")

async def cleanup_old_searches():
    while True:
        await asyncio.sleep(300)
        current_time = time.time()
        async with search_lock:
            to_remove = []
            for gid, info in search_map.items():
                if current_time - info.get('timestamp', 0) > 1800:
                    to_remove.append(gid)
            for gid in to_remove:
                if 'buttons_map' in search_map[gid]:
                    for bd in search_map[gid]['buttons_map']:
                        button_to_search.pop(bd, None)
                client_id = id(search_map[gid]['client'])
                if client_to_search.get(client_id) == gid:
                    del client_to_search[client_id]
                del search_map[gid]
            if to_remove:
                print(f"🧹 Limpiadas {len(to_remove)} búsquedas antiguas")

async def main():
    await init_sessions()
    for client in sessions_pool:
        await setup_handler(client)
    await bot.start(bot_token=BOT_TOKEN)
    print(f"✅ Music Bot en {GRUPO} - {len(SESSIONS)} sesiones")
    asyncio.create_task(cleanup_old_searches())
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
