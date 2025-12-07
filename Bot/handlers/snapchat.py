from pyrogram import Client, filters
from pyrogram.types import CallbackQuery
import yt_dlp
import os

def snapchat(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get('url')
            title = info.get('title', 'Snapchat Video')
            
            return {
                "success": True,
                "url": video_url,
                "title": title
            }
    except Exception as e:
        return {"success": False}


@Client.on_callback_query(filters.regex(r"^(snapchat)$"))
async def send(client: Client, callback: CallbackQuery):
    user_id = callback.message.from_user.id
    caption = "يمكنك ارسال الرابط الآن."
    answer = await callback.message.chat.ask(text=caption)
    await client.delete_messages(user_id, answer.id)
    processing_msg = await callback.message.reply_text("Processing...")
    url = answer.text
    
    response = snapchat(url)
    if not response["success"]:
        await processing_msg.delete()
        await callback.message.reply_text("الرابط غير صالح")
        return
    
    safe_title = "".join(c for c in response['title'] if c.isalnum() or c in (' ', '-', '_'))[:50]
    output_file = f"{safe_title}.mp4"
    
    ydl_opts = {
        'outtmpl': output_file,
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        bot = await client.get_me()
        bot_name = bot.first_name
        bot_url = f"{bot.username}.t.me"
        caption = f"● Uploaded By : [{bot_name}]({bot_url})"
        
        await callback.message.reply_video(
            video=output_file,
            caption=caption,
        )
        
        if os.path.exists(output_file):
            os.remove(output_file)
            
    except Exception as e:
        await callback.message.reply_text(f"حدث خطأ في التحميل")
    
    await processing_msg.delete()
