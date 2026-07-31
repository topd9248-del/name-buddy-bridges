import asyncio, re, os, time, threading, urllib.request
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from http.server import HTTPServer, BaseHTTPRequestHandler

API_ID = 28074212
API_HASH = "b18dae908474a377684922f3e9d5b795"
BOT_TOKEN = "8809406756:AAF89So4ySOmgy_rrb4jm_1TvW5h8cvgIm8"
SESSION = "1AZWarzQBux0PgvtpPGNQKu_oA9eWx0mFnbhJ8S6TKSXc4C82ka-SBzwbB5Y6ZKIf9_VY_8FcXiqXgA7ai8JL1o0kSkFuDPeBzXO-vpWglyGfbp-Ze-0btTbxR6Imea6vHFtyFDzyANOGqHqxvDOmfL5t0dN4cMAxpcdISzRBdvZ6L9wgmsDFFeIJNNVcCrTyftMHrs9L6fKLZ04fZnDZP7vCBSS-6nHVyEy_S9XrQ18mCKlCInmdewmpqWVI-LIZ6CYQj7ijtKRK4Bmgh4C7x0-F4N5Rtr_32ba7n5gdptIwEilBxeRRIDiJgC_3IF5Ggf2xecfu7zUzFKtHn8_r7YyG90ASqHM="
CHATBOT = "@CHAT_GTBOT"
CHATBOT_ID = 5963165469
GRUPO = "@BuddyMovies_official"

PREFIJO = """IMPORTANTE: Responde SOLO en español. No uses árabe ni inglés. Sé breve y directo.
Pon emojis a tus respuestas. Resalta las partes importantes con letra negrita. Sé profesional.
Responde atractivo. No uniformes nada más. No pongas "¿Quieres detalles de alguna en particular?"
Responde rápido."""

user_questions = {}

bot = TelegramClient('chatgpt_bot', API_ID, API_HASH, retry_delay=5, auto_reconnect=True, timeout=15)
user = TelegramClient(StringSession(SESSION), API_ID, API_HASH, retry_delay=5, auto_reconnect=True, timeout=15)

def clean_response(text):
    if not text: return ""
    text = text.replace("@SAMI_AIB", "").strip()
    text = text.replace("SAMI__AIB", "Buddy ConanIA")
    text = text.replace("SAMI_AIB", "Buddy ConanIA")
    text = text.replace("BEEB", "@BuddyMovies_official")
    text = text.replace("saudí Turki", "Conan")
    text = text.replace("Turki", "Conan")
    text = text.replace("saudí", "")
    text = text.replace("plataforma  bajo", "plataforma @BuddyMovies_official bajo")
    text = text.replace("la plataforma  bajo", "la plataforma @BuddyMovies_official bajo")
    text = re.sub(r'@(?!BuddyMovies)\w+', '', text)
    text = re.sub(r'https?://\S+', '', text)
    return text.strip()

@user.on(events.NewMessage(from_users=CHATBOT_ID))
async def on_response(event):
    m = event.message
    if not m.text: return
    if "please wait" in m.text.lower(): return
    
    clean = clean_response(m.text)
    
    for uid, data in list(user_questions.items()):
        await bot.send_message(
            GRUPO,
            f"🤖 **ChatGPT responde a {data['name']}:**\n\n"
            f"📝 **{data['question']}**\n\n"
            f"{clean[:2000]}",
            reply_to=data['reply_to']
        )
        del user_questions[uid]
        break
    print("✅ Respuesta enviada")

@bot.on(events.NewMessage)
async def on_user(event):
    if event.is_private or event.out or not event.text: return
    q = event.text.strip()
    if len(q) < 2 or q.startswith("/"): return
    
    try: name = (await event.get_sender()).first_name or "Usuario"
    except: name = "Usuario"
    
    user_questions[event.sender_id] = {'name': name, 'question': q, 'reply_to': event.message.id}
    prompt = f"{PREFIJO}\n\n{name} puso esto:\n\n: {q}"
    print(f"📤 {name}: {q}")
    await user.send_message(CHATBOT, prompt)

async def main():
    await user.start()
    await bot.start(bot_token=BOT_TOKEN)
    print("✅ ChatGPT Buddy activo")
    await asyncio.gather(bot.run_until_disconnected(), user.run_until_disconnected())

# Anti-sleep
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
