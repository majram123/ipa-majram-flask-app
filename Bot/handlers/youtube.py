from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp
import asyncio
import os
import time

youtube_user_data = {}

async def youtube_fetch(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
    }
    
    try:
        loop = asyncio.get_event_loop()
        def extract():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(url, download=False)
        
        info = await loop.run_in_executor(None, extract)
        title = info.get('title', 'YouTube Video')
        uploader = info.get('uploader', 'unknown')
        
        return {
            "success": True,
            "title": title,
            "uploader": uploader,
            "url": url
        }
    except Exception:
        return {"success": False}

async def youtube_download(url, output_file, format_opt='best[ext=mp4]/best'):
    ydl_opts = {
        'outtmpl': output_file,
        'quiet': True,
        'no_warnings': True,
        'format': format_opt,
        'concurrent_fragment_downloads': 10,
        'http_chunk_size': 4194304,
        'retries': 5,
        'fragment_retries': 5,
    }
    
    try:
        loop = asyncio.get_event_loop()
        def download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        
        await loop.run_in_executor(None, download)
        return True
    except Exception:
        return False

async def youtube_download_audio(url, base_name):
    ydl_opts = {
        'outtmpl': base_name,
        'quiet': True,
        'no_warnings': True,
        'format': 'bestaudio/best',
        'concurrent_fragment_downloads': 10,
        'http_chunk_size': 4194304,
        'retries': 5,
        'fragment_retries': 5,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    
    try:
        loop = asyncio.get_event_loop()
        def download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        
        await loop.run_in_executor(None, download)
        return True
    except Exception:
        return False

@Client.on_callback_query(filters.regex(r"^(youtube)$"))
async def youtube_send(client: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    caption = "يمكنك ارسال الرابط الآن."
    answer = await callback.message.chat.ask(text=caption)
    
    try:
        await client.delete_messages(callback.message.chat.id, answer.id)
    except:
        pass
    
    processing_msg = await callback.message.reply_text("جاري المعالجة...")
    url = answer.text
    
    response = await youtube_fetch(url)
    if not response["success"]:
        await processing_msg.delete()
        await callback.message.reply_text("الرابط غير صالح")
        return
    
    youtube_user_data[user_id] = response
    
    os.makedirs("Bot/downloads", exist_ok=True)
    output_file = f"Bot/downloads/yt_{user_id}_{int(time.time())}.mp4"
    
    try:
        success = await youtube_download(url, output_file)
        if not success:
            await processing_msg.delete()
            await callback.message.reply_text("حدث خطأ في التحميل")
            return
        
        bot = await client.get_me()
        bot_name = bot.first_name
        bot_url = f"{bot.username}.t.me"
        caption = f"● title : {response['title']}\n\n● Uploaded By : [{bot_name}]({bot_url})"
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("تحميل بدقه HD", callback_data=f"download_yt_hd_{user_id}"),
                InlineKeyboardButton("ملف صوتي", callback_data=f"download_yt_audio_{user_id}")
            ]
        ])
        
        await callback.message.reply_video(
            video=output_file,
            caption=caption,
            reply_markup=keyboard
        )
        
        if os.path.exists(output_file):
            os.remove(output_file)
            
    except Exception:
        await callback.message.reply_text("حدث خطأ في التحميل")
    
    await processing_msg.delete()


@Client.on_callback_query(filters.regex(r"^download_yt_hd_(\d+)$"))
async def youtube_download_hd(client: Client, callback: CallbackQuery):
    user_id = int(callback.data.split("_")[3])
    
    if user_id not in youtube_user_data:
        await callback.answer("انتهت صلاحية البيانات، يرجى إعادة المحاولة", show_alert=True)
        return
    
    await callback.answer("جاري بدء التحميل...")
    
    data = youtube_user_data[user_id]
    processing_msg = await callback.message.reply_text("جاري تحميل الفيديو بدقة HD...")
    
    try:
        os.makedirs("Bot/downloads", exist_ok=True)
        output_file = f"Bot/downloads/yt_hd_{user_id}_{int(time.time())}.mp4"
        
        success = await youtube_download(
            data['url'], 
            output_file, 
            'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        )
        if not success:
            await processing_msg.delete()
            await callback.message.reply_text("حدث خطأ في التحميل")
            return
        
        bot = await client.get_me()
        bot_name = bot.first_name
        bot_url = f"{bot.username}.t.me"
        caption = f"● title : {data['title']}\n\n● Uploaded By : [{bot_name}]({bot_url})"
        
        await callback.message.reply_video(
            video=output_file,
            caption=caption,
        )
        
        if os.path.exists(output_file):
            os.remove(output_file)
        
        await processing_msg.delete()
        
    except Exception:
        await processing_msg.delete()
        await callback.message.reply_text("حدث خطأ في التحميل")


@Client.on_callback_query(filters.regex(r"^download_yt_audio_(\d+)$"))
async def youtube_download_audio_handler(client: Client, callback: CallbackQuery):
    user_id = int(callback.data.split("_")[3])
    
    if user_id not in youtube_user_data:
        await callback.answer("انتهت صلاحية البيانات، يرجى إعادة المحاولة", show_alert=True)
        return
    
    await callback.answer("جاري بدء التحميل...")
    
    data = youtube_user_data[user_id]
    processing_msg = await callback.message.reply_text("جاري تحميل الملف الصوتي...")
    
    try:
        os.makedirs("Bot/downloads", exist_ok=True)
        base_name = f"Bot/downloads/yt_audio_{user_id}_{int(time.time())}"
        output_file = f"{base_name}.mp3"
        
        success = await youtube_download_audio(data['url'], base_name)
        if not success:
            await processing_msg.delete()
            await callback.message.reply_text("حدث خطأ في التحميل")
            return
        
        bot = await client.get_me()
        bot_name = bot.first_name
        bot_url = f"{bot.username}.t.me"
        caption = f"● title : {data['title']}\n\n● Uploaded By : [{bot_name}]({bot_url})"
        
        await callback.message.reply_audio(
            audio=output_file,
            caption=caption,
            title=data['title']
        )
        
        if os.path.exists(output_file):
            os.remove(output_file)
        
        await processing_msg.delete()
        
    except Exception as e:
        print(f"Error: {e}")
        await processing_msg.delete()
        await callback.message.reply_text("حدث خطأ في التحميل")
