from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import aiohttp
import aiofiles
import asyncio
import os
import time

tiktok_user_data = {}

async def tiktok_fetch(url, quality="hd"):
    try:
        headers = {
            'authority': 'api.tikmate.app',
            'accept': '*/*',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://tikmate.app',
            'referer': 'https://tikmate.app/',
            'user-agent': 'Mozilla/5.0'
        }
        data = {'url': url}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                'https://api.tikmate.app/api/lookup', 
                headers=headers, 
                data=data, 
                ssl=False, 
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                r = await response.json()

        if not r.get('success'):
            return {"success": False}

        q = "hd=1" if quality == "hd" else "hd=0"
        video_url = f"https://tikmate.app/download/{r['token']}/{r['id']}.mp4?{q}"
        audio_url = f"https://tikmate.app/download/{r['token']}/{r['id']}.mp3"

        return {
            "success": True,
            "title": r.get('title', 'TikTok Video'),
            "video_url": video_url,
            "audio_url": audio_url,
            "token": r['token'],
            "id": r['id']
        }

    except Exception:
        return {"success": False}

async def download_file_async(url, output_path, chunk_size=131072):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, ssl=False, timeout=aiohttp.ClientTimeout(total=300)) as response:
                response.raise_for_status()
                async with aiofiles.open(output_path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(chunk_size):
                        await f.write(chunk)
        return True
    except Exception:
        return False

@Client.on_callback_query(filters.regex(r"^(tiktok)$"))
async def tiktok_send(client: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    caption = "يمكنك ارسال الرابط الآن."
    answer = await callback.message.chat.ask(text=caption)
    
    try:
        await client.delete_messages(callback.message.chat.id, answer.id)
    except:
        pass
    
    processing_msg = await callback.message.reply_text("جاري المعالجة...")
    url = answer.text

    response = await tiktok_fetch(url, quality="hd")
    if not response["success"]:
        await processing_msg.delete()
        await callback.message.reply_text("الرابط غير صالح")
        return

    tiktok_user_data[user_id] = response

    os.makedirs("Bot/downloads", exist_ok=True)
    output_file = f"Bot/downloads/tt_{user_id}_{int(time.time())}.mp4"

    try:
        success = await download_file_async(response['video_url'], output_file)
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
                InlineKeyboardButton("تحميل بدقه HD", callback_data=f"download_tt_hd_{user_id}"),
                InlineKeyboardButton("ملف صوتي", callback_data=f"download_tt_audio_{user_id}")
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


@Client.on_callback_query(filters.regex(r"^download_tt_hd_(\d+)$"))
async def tiktok_download_hd(client: Client, callback: CallbackQuery):
    user_id = int(callback.data.split("_")[3])

    if user_id not in tiktok_user_data:
        await callback.answer("انتهت صلاحية البيانات، يرجى إعادة المحاولة", show_alert=True)
        return

    await callback.answer("جاري بدء التحميل...")
    
    data = tiktok_user_data[user_id]
    processing_msg = await callback.message.reply_text("جاري تحميل الفيديو بدقة HD...")

    try:
        os.makedirs("Bot/downloads", exist_ok=True)
        output_file = f"Bot/downloads/tt_hd_{user_id}_{int(time.time())}.mp4"

        success = await download_file_async(data['video_url'], output_file)
        if not success:
            await processing_msg.delete()
            await callback.answer("حدث خطأ في التحميل", show_alert=True)
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
        await callback.answer("حدث خطأ في التحميل", show_alert=True)


@Client.on_callback_query(filters.regex(r"^download_tt_audio_(\d+)$"))
async def tiktok_download_audio(client: Client, callback: CallbackQuery):
    user_id = int(callback.data.split("_")[3])

    if user_id not in tiktok_user_data:
        await callback.answer("انتهت صلاحية البيانات، يرجى إعادة المحاولة", show_alert=True)
        return

    await callback.answer("جاري بدء التحميل...")
    
    data = tiktok_user_data[user_id]
    processing_msg = await callback.message.reply_text("جاري تحميل الملف الصوتي...")

    try:
        os.makedirs("Bot/downloads", exist_ok=True)
        output_file = f"Bot/downloads/tt_audio_{user_id}_{int(time.time())}.mp3"

        success = await download_file_async(data['audio_url'], output_file)
        if not success:
            await processing_msg.delete()
            await callback.answer("حدث خطأ في التحميل", show_alert=True)
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

    except Exception:
        await processing_msg.delete()
        await callback.answer("حدث خطأ في التحميل", show_alert=True)
