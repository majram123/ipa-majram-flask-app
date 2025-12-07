from pyrogram import Client, filters
from pyrogram.types import CallbackQuery
import yt_dlp
import os

def soundcloud(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'SoundCloud Audio')
            uploader = info.get('uploader', 'unknown')
            likes = info.get('like_count', 0)
            audio_url = info.get('url')
            
            return {
                "success": True,
                "mp3": audio_url,
                "title": title,
                "username": uploader,
                "likes": likes
            }
    except Exception as e:
        return {"success": False}


@Client.on_callback_query(filters.regex(r"^(soundcloud)$"))
async def send(client: Client, callback: CallbackQuery):
    user_id = callback.message.from_user.id
    caption = "يمكنك ارسال الرابط الآن."
    answer = await callback.message.chat.ask(text=caption)
    await client.delete_messages(user_id, answer.id)
    processing_msg = await callback.message.reply_text("Processing...")
    url = answer.text
    
    try:
        response = soundcloud(url)
    except Exception as e:
        await processing_msg.delete()
        await callback.message.reply_text("الرابط غير صالح")
        return
    
    if not response.get("success"):
        await processing_msg.delete()
        await callback.message.reply_text("الرابط غير صالح")
        return
    
    safe_title = "".join(c for c in response['title'] if c.isalnum() or c in (' ', '-', '_'))[:50]
    output_file = f"{safe_title}.mp3"
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': safe_title,
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        bot = await client.get_me()
        bot_name = bot.first_name
        bot_url = f"{bot.username}.t.me"
        caption = f"● title : {response['title']}\n● Likes : {response['likes']}\n\n● Uploaded By : [{bot_name}]({bot_url})"
        
        await callback.message.reply_audio(
            audio=output_file,
            caption=caption,
        )
        
        if os.path.exists(output_file):
            os.remove(output_file)
            
    except Exception as e:
        await callback.message.reply_text(f"حدث خطأ في التحميل")
    
    await processing_msg.delete()
