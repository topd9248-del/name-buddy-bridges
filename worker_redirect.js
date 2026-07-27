const TOKEN = '8819823110:AAFiP3VLjRy5BLZvFozUL0F3cORSI1TZLGE';
const TG = `https://api.telegram.org/bot${TOKEN}`;
const GRUPO = 'https://t.me/BuddyMovies_official';
const CANAL = 'https://t.me/BuddyMovies_canal';

const MSG = `🎬 *Join to search movies & series!*

📢 *Join our group:* ${GRUPO}
📺 *Join our channel:* ${CANAL}

✨ *After joining, just type a movie name and I'll find it for you!*`;

export default {
  async fetch(request) {
    if (request.method !== 'POST') return new Response('OK');
    
    try {
      const body = await request.json();
      const msg = body.message;
      
      if (!msg?.text) return new Response('OK');
      
      const chat_id = msg.chat.id;
      const chat_type = msg.chat.type;
      const msg_id = msg.message_id;
      const text = msg.text.trim();
      
      // Comando start en privado
      if (text === '/start') {
        await fetch(`${TG}/sendMessage`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            chat_id,
            text: `🎬 *Welcome!*\n\n📢 *Join to search:* ${GRUPO}\n📺 *Channel:* ${CANAL}`,
            parse_mode: 'Markdown',
            reply_markup: JSON.stringify({
              inline_keyboard: [
                [{ text: '📢 JOIN GROUP', url: GRUPO }],
                [{ text: '📺 JOIN CHANNEL', url: CANAL }]
              ]
            })
          })
        });
        return new Response('OK');
      }
      
      // Si es grupo, enviar mensaje y borrar el original
      if (chat_type === 'group' || chat_type === 'supergroup') {
        try {
          await fetch(`${TG}/deleteMessage`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ chat_id, message_id: msg_id })
          });
        } catch (e) {}
        
        await fetch(`${TG}/sendMessage`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            chat_id,
            text: MSG,
            parse_mode: 'Markdown',
            reply_markup: JSON.stringify({
              inline_keyboard: [
                [{ text: '📢 JOIN GROUP', url: GRUPO }],
                [{ text: '📺 JOIN CHANNEL', url: CANAL }]
              ]
            })
          })
        });
      }
      
      return new Response('OK');
    } catch (e) {
      return new Response('OK');
    }
  }
};
