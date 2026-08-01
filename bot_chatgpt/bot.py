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

PREFIJO = """▎Instrucciones de Respuesta (Versión Final)

Se breve no pongas @ no pongas demasiadas líneas resalta las palabras más importantes

Responde siempre en español, de forma amable y profesional. Usa emojis de manera natural 😊.

▎Lógica de Detección

1.  Si es una PELÍCULA ESPECÍFICA: Usa el Formato Individual 🎬.
2.  Si es una CATEGORÍA o SAGA (Ej: "Tortugas Ninja"): Usa el Formato de Saga 🗂️.

▎Formato para Películas Individuales 🎬
Usa esto solo si el título es concreto:
1.  🎬 Género: [Texto]
2.  ⭐ Protagonistas: [Texto]
3.  📝 Trama breve: [Texto]
4.  🔎 Características: [Texto]
5.  👍 Recomendación: [Texto]

▎Formato para Categorías y Sagas 🗂️
Usa esto si mencionan un grupo de películas o una franquicia general:
1.  🎨 Origen y Creadores: Quiénes los crearon y la empresa/estudio original.
2.  🌍 Trama General: De qué trata la franquicia de forma global.
3.  👥 Personajes Principales: Lista de protagonistas clave.
4.  🏆 Hito de la Saga: Cuál es la película más vista o exitosa en taquilla.
5.  🍿 Listado Sugerido: Una lista numerada de 4-5 películas importantes con un mini resumen de cada una.

▎Organización y Reglas
• Menciona al usuario: Si sabes quién pregunta, empieza con un "Hola Nombre".
• Multiusuario: Si varias personas preguntan a la vez, separa las respuestas claramente con una línea o título.
• Enriquecimiento: Actúa como un experto. Si el tema es general, aporta datos interesantes sobre el impacto de la obra o la empresa.
• Orden: Responde en el mismo orden en que llegaron las preguntas."""

user_questions = {}
sent_messages = {}

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
    text = re.sub(r'@(?!BuddyMovies)\w+', '', text)
    text = re.sub(r'https?://\S+', '', text)
    return text.strip()

@user.on(events.NewMessage(from_users=CHATBOT_ID))
async def on_response(event):
    m = event.message
    if not m.text: return
    if "please wait" in m.text.lower(): return
    if "used up your credits" in m.text.lower(): return
    if "upgrade to coze premium" in m.text.lower(): return
    
    clean = clean_response(m.text)
    
    for uid, data in list(user_questions.items()):
        header = f"🤖 **ChatGPT responde a {data['name']}:**\n\n📝 **{data['question']}**\n\n"
        if uid in sent_messages:
            # Si ya enviamos, editar
            try:
                await bot.edit_message(GRUPO, sent_messages[uid], header + clean)
                print(f"✏️ Editado: {len(clean)} chars")
            except:
                pass
        else:
            # Primera vez, enviar nuevo
            sent = await bot.send_message(GRUPO, header + clean, reply_to=data['reply_to'])
            sent_messages[uid] = sent.id
            print(f"✅ Enviado: {len(clean)} chars")

@user.on(events.MessageEdited(from_users=CHATBOT_ID))
async def on_edit(event):
    pass  # La edición se maneja en on_response

@bot.on(events.NewMessage)
async def on_user(event):
    if event.is_private or event.out or not event.text: return
    q = event.text.strip()
    if len(q) < 2 or q.startswith("/"): return
    
    try: name = (await event.get_sender()).first_name or "Usuario"
    except: name = "Usuario"
    
    user_questions[event.sender_id] = {'name': name, 'question': q, 'reply_to': event.message.id}
    prompt = f"{PREFIJO}\n\n{name} puso esto:\n\n: {q}"
    await user.send_message(CHATBOT, prompt)

async def main():
    await user.start()
    await bot.start(bot_token=BOT_TOKEN)
    print("✅ ChatGPT Buddy activo")
    await asyncio.gather(bot.run_until_disconnected(), user.run_until_disconnected())

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
