import os, yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = '6749937881:AAE8JcKVATr6qYC5FpmwiyhANRljzcCHAMw'

async def h_msg(u: Update, c: ContextTypes.DEFAULT_TYPE):
    q = u.message.text if u.message.text else 'បទចម្រៀង'
    kb = [
        [InlineKeyboardButton('🎵 128kbps', callback_data=f'd|128|{q}'), InlineKeyboardButton('🎧 320kbps', callback_data=f'd|320|{q}')],
        [InlineKeyboardButton('🎤 Karaoke (ភ្លេងសុទ្ធ)', callback_data=f'k|128|{q}')],
        [InlineKeyboardButton('⏯ Preview 30s', callback_data=f'p|128|{q}')]
    ]
    await u.message.reply_text(f'🎼 បទ: {q}\nសូមជ្រើសរើសមុខងារ៖', reply_markup=InlineKeyboardMarkup(kb))

async def cb(u: Update, c: ContextTypes.DEFAULT_TYPE):
    q = u.callback_query
    await q.answer()
    act, br, s = q.data.split('|')
    m = await c.bot.send_message(q.message.chat_id, '🚀 កំពុងដំណើរការ... សូមរង់ចាំ!')
    
    opts = {'format': 'bestaudio/best', 'outtmpl': 'downloads/%(title)s.%(ext)s', 'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': br}]}
    if act == 'p': opts['postprocessor_args'] = ['-ss', '00:00:00', '-t', '00:00:30']

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(f'ytsearch1:{s}', download=True)
            if 'entries' in info: info = info['entries'][0]
            p = ydl.prepare_filename(info).replace(info['ext'], 'mp3')
            t = info.get('title')
            if act == 'k': t = f'🎤 [Karaoke] {t}'
            
            with open(p, 'rb') as f: await c.bot.send_audio(chat_id=q.message.chat_id, audio=f, title=t, caption='🌟 @CBTA_Network')
            if os.path.exists(p): os.remove(p)
            await m.delete()
    except Exception as e: await m.edit_text(f'❌ Error: {str(e)}')

def main():
    if not os.path.exists('downloads'): os.makedirs('downloads')
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT | filters.VOICE, h_msg))
    app.add_handler(CallbackQueryHandler(cb))
    print('--- Bot Karaoke & MP3 Is Running ---')
    app.run_polling()

if __name__ == '__main__': main()
