import asyncio, re, os, time, threading, urllib.request
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from http.server import HTTPServer, BaseHTTPRequestHandler

API_ID = 28074212
API_HASH = "b18dae908474a377684922f3e9d5b795"
BOT_TOKEN = "8809406756:AAF89So4ySOmgy_rrb4jm_1TvW5h8cvgIm8"

# 4 sesiones para rotar
SESSIONS = [
    "1AZWarzQBux0PgvtpPGNQKu_oA9eWx0mFnbhJ8S6TKSXc4C82ka-SBzwbB5Y6ZKIf9_VY_8FcXiqXgA7ai8JL1o0kSkFuDPeBzXO-vpWglyGfbp-Ze-0btTbxR6Imea6vHFtyFDzyANOGqHqxvDOmfL5t0dN4cMAxpcdISzRBdvZ6L9wgmsDFFeIJNNVcCrTyftMHrs9L6fKLZ04fZnDZP7vCBSS-6nHVyEy_S9XrQ18mCKlCInmdewmpqWVI-LIZ6CYQj7ijtKRK4Bmgh4C7x0-F4N5Rtr_32ba7n5gdptIwEilBxeRRIDiJgC_3IF5Ggf2xecfu7zUzFKtHn8_r7YyG90ASqHM=",
    "1AZWarzcBu7NWttiJjYomqupi0XGpOJ5CyTJaMLedXyc8o86qAI7wBFwPDVBLhYqIqScZa3YGLstCdP0P6Bw9dYnj1D0zmkGsGCCKjqbnBPCpgUpdT4PiOQ_TJTwJ-WHUnyKLM9_qfinV88uBuHiymc6pFRwDquBilCRwIu6ABkflwxwjiSttzm1mcdO0nF10nU8Ytw1l4v9uGCSv1PA_nwdFkGlDrqnO17ltCQHKpN3aSijsUtItmpPBvV_LezUcGaZB9DbgQcBZF_Scoe68NJxWlZOGOLvc4kh_EXKj8pH-ffVNNBwIzXSSOHhqpZYhappPxo4gec_yL4MfJPikiWabNcAK_lQ=",
    "1AZWarzcBuwdx0jHcxtjk44SE_RCEMthQYDwuUU47oszDZ6H48tRyhmFEsbLJVC2Ib1biQIJfP43EO1GLHRXuiKNUUiw1546agDENm7oCwAszTV6-dAcSLFJoT1vfvt2gc749ZwAgf-Rt93ejqcc_pDExP4x260d7GVCXmdmuQCQnwfxYt3levb7DXHmK4B5v4xFAZIvsUNhQJktPtHu3Z0pGNz0ckKL97eOPcroPyXvjkq0PF821BY2y13iFcsX7ngQSU3m-51C6EP8GCUDZlE4Wm1CKweiSSwyY0zU3xwzn45JJ2-ysQWUo1ZGqOcqqI6_BNO6C1MO2iSJb7nlbG0xuARFt2sk=",
    "1AZWarzcBu0MRa5sKIdd7g4cG3sPDxxnGfa9IPC3RS7kfi5nw99fWZCZt4PGRfZD-eyG5gKoFg0VrBMTRSLcfDC0qKWdLiAZJvwiQ744js0LHva6XrPSqOwBi8QD5iwGVaKe8N5rH1Whb9EHWXGoP404VgrMbfOiMG5tuS4bUvfKXMOAMEjLv7rwnAu92jb3dtWjxQCVJJkQGV8Oj1Enw5R8uRqSABK2IkgSX4w7UVAteEpM_NXHRQIaKSbBuFaTRIoUT-9JfoUbcmPplPIfnCYg3QAW6PE-2Np2By5jDd3CBZbXOTRqRJ7jvbYjcM1xj0HxX3HpnYheyXXfhNAF1al4C-unIL2E="
]

current_session = 0
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
last_question_uid = None
sent_messages = {}

bot = TelegramClient('chatgpt_bot', API_ID, API_HASH, retry_delay=5, auto_reconnect=True, timeout=15)
user = None

def get_user_client():
    global current_session
    session = SESSIONS[current_session]
    return TelegramClient(StringSession(session), API_ID, API_HASH, retry_delay=5, auto_reconnect=True, timeout=15)

async def switch_session():
    global current_session, user
    current_session = (current_session + 1) % len(SESSIONS)
    print(f"🔄 Cambiando a sesión {current_session + 1}/{len(SESSIONS)}")
    try:
        await user.disconnect()
    except: pass
    user = get_user_client()
    await user.start()
    setup_handlers()
    print(f"✅ Sesión {current_session + 1} activa")

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

async def send_or_edit(clean, uid=None):
    if not uid:
        # Si no se especifica, usar el primero (para ediciones)
        if user_questions:
            uid = list(user_questions.keys())[0]
        else:
            return
    
    data = user_questions.get(uid)
    if not data: return
    
    header = f"🤖 **ChatGPT responde a {data['name']}:**\n\n📝 **{data['question']}**\n\n"
    if uid in sent_messages:
        try:
            await bot.edit_message(GRUPO, sent_messages[uid], header + clean)
            print(f"✏️ Editado para {data['name']}: {len(clean)} chars")
        except:
            sent = await bot.send_message(GRUPO, header + clean, reply_to=data['reply_to'])
            sent_messages[uid] = sent.id
    else:
        sent = await bot.send_message(GRUPO, header + clean, reply_to=data['reply_to'])
        sent_messages[uid] = sent.id
        print(f"✅ Enviado a {data['name']}: {len(clean)} chars")

def setup_handlers():
    @user.on(events.NewMessage(from_users=CHATBOT_ID))
    async def on_response(event):
        m = event.message
        if not m.text: return
        if "please wait" in m.text.lower(): return
        
        # Detectar créditos agotados -> cambiar sesión
        if "used up your credits" in m.text.lower() or "upgrade to coze premium" in m.text.lower():
            print("⚠️ Créditos agotados - cambiando sesión...")
            await switch_session()
            # Reenviar la pregunta pendiente
            for uid, data in list(user_questions.items()):
                prompt = f"{PREFIJO}\n\n{data['name']} puso esto:\n\n: {data['question']}"
                await user.send_message(CHATBOT, prompt)
                print(f"🔄 Reenviado a nueva sesión: {data['question']}")
                break
            return
        
        clean = clean_response(m.text)
        await send_or_edit(clean, last_question_uid)

    @user.on(events.MessageEdited(from_users=CHATBOT_ID))
    async def on_edit(event):
        m = event.message
        if not m.text: return
        if "used up your credits" in m.text.lower(): return
        clean = clean_response(m.text)
        await send_or_edit(clean, last_question_uid)

@bot.on(events.NewMessage)
async def on_user(event):
    if event.is_private or event.out or not event.text: return
    q = event.text.strip()
    if len(q) < 2 or q.startswith("/"): return
    
    try: name = (await event.get_sender()).first_name or "Usuario"
    except: name = "Usuario"
    
    if event.sender_id in sent_messages:
        del sent_messages[event.sender_id]
    
    user_questions[event.sender_id] = {'name': name, 'question': q, 'reply_to': event.message.id}
    global last_question_uid
    last_question_uid = event.sender_id
    prompt = f"{PREFIJO}\n\n{name} puso esto:\n\n: {q}"
    await user.send_message(CHATBOT, prompt)

async def main():
    global user
    user = get_user_client()
    await user.start()
    setup_handlers()
    await bot.start(bot_token=BOT_TOKEN)
    print(f"✅ ChatGPT Buddy activo - Sesión {current_session + 1}")
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
