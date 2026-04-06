import os, yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# កូដសម្គាល់ Bot របស់បង
TOKEN = '6749937881:AAE8JcKVATr6qYC5FpmwiyhANRljzcCHAMw'

async def h_msg(u: Update, c: ContextTypes.DEFAULT_TYPE):
    query = u.message.text
    if not query: return
    
    m = await u.message.reply_text(f"🔍 កំពុងស្វែងរកបទ '{query}' ចំនួន ១០ បទដែលល្អបំផុត...")
    
    # កំណត់ការស្វែងរក ១០ បទ
    ydl_opts = {'extract_flat': True, 'quiet': True, 'no_warnings': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_results = ydl.extract_info(f"ytsearch10:{query}", download=False)
            if 'entries' not in search_results or not search_results['entries']:
                await m.edit_text("❌ រកមិនឃើញបទចម្រៀងនេះទេ បងសាកប្ដូរឈ្មោះបទថ្មីមើល៍!")
                return

            keyboard = []
            for i, entry in enumerate(search_results['entries']):
                title = entry.get('title')
                # កាត់ចំណងជើងឱ្យខ្លីបន្តិចដើម្បីឱ្យស្អាតលើប៊ូតុង
                short_title = (title[:35] + '..') if len(title) > 35 else title
                v_id = entry.get('id')
                # បង្កើតប៊ូតុងបញ្ជីឈ្មោះបទ
                keyboard.append([InlineKeyboardButton(f"{i+1}. {short_title}", callback_data=f"sel|{v_id}")])
            
            await m.edit_text(f"🎼 លទ្ធផលស្វែងរកសម្រាប់: {query}\nសូមជ្រើសរើសបទដែលបងចង់បាន៖", 
                              reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception:
        await m.edit_text("❌ មានបញ្ហាបច្ចេកទេសក្នុងការស្វែងរក។ សូមព្យាយាមម្ដងទៀត!")

async def cb(u: Update, c: ContextTypes.DEFAULT_TYPE):
    query = u.callback_query
    await query.answer()
    data = query.data.split('|')
    
    if data[0] == 'sel':
        v_id = data[1]
        # ប៊ូតុងសម្រាប់រើសប្រភេទ MP3 ឬ Karaoke
        kb = [[
            InlineKeyboardButton('🎵 ទាញយក MP3', callback_data=f'dl|128|{v_id}'),
            InlineKeyboardButton('🎤 ភ្លេងសុទ្ធ (Karaoke)', callback_data=f'dl|320|{v_id}')
        ]]
        await query.edit_message_text("ជ្រើសរើសប្រភេទដែលបងចង់បាន៖", reply_markup=InlineKeyboardMarkup(kb))
        
    elif data[0] == 'dl':
        br, v_id = data[1], data[2]
        m = await c.bot.send_message(query.message.chat_id, "🚀 កំពុងទាញយកបទចម្រៀង... បទវែងអាចប្រើពេលបន្តិចណា!")
        
        # កំណត់ការទាញយក (បន្លំ YouTube និងយកបទពេញ)
        opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': br}],
            'quiet': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        }

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(f"https://www.youtube.com/watch?v={v_id}", download=True)
                path = ydl.prepare_filename(info).replace(info['ext'], 'mp3')
                
                with open(path, 'rb') as f:
                    await c.bot.send_audio(
                        chat_id=query.message.chat_id, 
                        audio=f, 
                        title=info.get('title'), 
                        caption=f"🌟 បទ: {info.get('title')}\n✅ រួចរាល់ហើយបង!"
                    )
                
                if os.path.exists(path): os.remove(path)
                await m.delete()
        except Exception as e:
            await m.edit_text(f"❌ មិនអាចទាញយកបានទេ! ប្រហែលមកពី YouTube ចាក់សោ។")

def main():
    if not os.path.exists('downloads'): os.makedirs('downloads')
    app = Application.builder().token(TOKEN).build()
    # ស្ដាប់រាល់សារជាអក្សរដែលផ្ញើមក
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, h_msg))
    app.add_handler(CallbackQueryHandler(cb))
    print("--- Bot កំពុងដំណើរការយ៉ាងរលូន ---")
    app.run_polling()

if __name__ == '__main__':
    main()
