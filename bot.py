import os, yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# កូដសម្គាល់ Bot
TOKEN = '6749937881:AAE8JcKVATr6qYC5FpmwiyhANRljzcCHAMw'

async def h_msg(u: Update, c: ContextTypes.DEFAULT_TYPE):
    query = u.message.text
    if not query: return
    m = await u.message.reply_text(f"🔍 កំពុងស្វែងរកបទ '{query}'...")
    ydl_opts = {'extract_flat': True, 'quiet': True, 'no_warnings': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            res = ydl.extract_info(f"ytsearch10:{query} official", download=False)
            if 'entries' not in res or not res['entries']:
                await m.edit_text("❌ រកមិនឃើញទេ!")
                return
            kb = [[InlineKeyboardButton(f"{i+1}. {e.get('title', 'Unknown')[:35]}", callback_data=f"sel|{e.get('id')}")] for i, e in enumerate(res['entries']) if e]
            await m.edit_text(f"🎼 លទ្ធផលសម្រាប់: {query}", reply_markup=InlineKeyboardMarkup(kb))
    except:
        await m.edit_text("❌ បញ្ហាស្វែងរក!")

async def cb(u: Update, c: ContextTypes.DEFAULT_TYPE):
    q = u.callback_query
    await q.answer()
    d = q.data.split('|')
    if d[0] == 'sel':
        kb = [[InlineKeyboardButton('🎵 MP3 (128k)', callback_data=f'dl|128|{d[1]}'), InlineKeyboardButton('🎤 Karaoke (320k)', callback_data=f'dl|320|{d[1]}')]]
        await q.edit_message_text("ជ្រើសរើសប្រភេទ៖", reply_markup=InlineKeyboardMarkup(kb))
    elif d[0] == 'dl':
        br, v_id = d[1], d[2]
        m = await c.bot.send_message(q.message.chat_id, "🚀 កំពុងទាញយក...")
        opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'restrictfilenames': True,
            'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': br}],
            'quiet': True
        }
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                v_url = f"https://www.youtube.com/watch?v={v_id}"
                info = ydl.extract_info(v_url, download=True)
                p = ydl.prepare_filename(info).replace(info['ext'], 'mp3')
                with open(p, 'rb') as f:
                    await c.bot.send_audio(chat_id=q.message.chat_id, audio=f, title=info.get('title'))
                if os.path.exists(p): os.remove(p)
                await m.delete()
        except:
            await m.edit_text("❌ មិនអាចទាញយកបាន!")

def main():
    if not os.path.exists('downloads'): os.makedirs('downloads')
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, h_msg))
    app.add_handler(CallbackQueryHandler(cb))
    app.run_polling()

if __name__ == '__main__':
    main()
