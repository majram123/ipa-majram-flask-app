from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import aiohttp
import aiofiles
import asyncio
import os
import json
import time
import subprocess
from datetime import datetime

ig_client = None
instagram_user_data = {}
last_session_update = None
SESSION_UPDATE_INTERVAL = 1800
MAX_LOGIN_RETRIES = 3

try:
    from instagrapi import Client as IGClient
    from instagrapi.exceptions import LoginRequired, ChallengeRequired
    INSTAGRAPI_AVAILABLE = True
except ImportError:
    INSTAGRAPI_AVAILABLE = False


def load_instagram_account():
    try:
        with open('Bot/database/instagram_cookies.json', 'r') as f:
            return json.load(f)
    except:
        return {"username": "", "password": ""}


def save_session():
    global ig_client
    if ig_client:
        try:
            session_file = 'Bot/database/instagram_session.json'
            ig_client.dump_settings(session_file)
            print("Instagram session saved")
        except Exception as e:
            print(f"Session save error: {e}")


def clear_session():
    session_file = 'Bot/database/instagram_session.json'
    if os.path.exists(session_file):
        try:
            os.remove(session_file)
            print("Old session cleared")
        except:
            pass


def keep_session_alive():
    global ig_client, last_session_update
    try:
        if ig_client:
            ig_client.get_timeline_feed()
            save_session()
            last_session_update = datetime.now()
            print("Instagram session refreshed")
            return True
    except Exception as e:
        print(f"Session expired: {e}")
        ig_client = None
        return False
    return False


def force_new_login():
    global ig_client, last_session_update
    
    if not INSTAGRAPI_AVAILABLE:
        return False
    
    clear_session()
    ig_client = None
    
    ig_client = IGClient()
    ig_client.set_device({
        "app_version": "269.0.0.18.75",
        "android_version": 26,
        "android_release": "8.0.0",
        "dpi": "480dpi",
        "resolution": "1080x1920",
        "manufacturer": "Apple",
        "device": "iPhone14,5",
        "model": "iPhone 14",
        "cpu": "A15 Bionic",
        "version_code": "314665256"
    })
    ig_client.set_user_agent(
        "Instagram 269.0.0.18.75 (iPhone14,5; iOS 18_0; en_IQ; en-IQ; scale=3.00; 1170x2532; 314665256)"
    )
    ig_client.set_locale("en_IQ")
    ig_client.set_timezone_offset(10800)

    account = load_instagram_account()
    if account.get('username') and account.get('password'):
        try:
            ig_client.login(account['username'], account['password'])
            ig_client.dump_settings('Bot/database/instagram_session.json')
            last_session_update = datetime.now()
            print("Instagram fresh login successful")
            return True
        except Exception as e:
            print(f"Instagram fresh login failed: {e}")
            ig_client = None
            return False
    return False


def login_instagram():
    global ig_client, last_session_update
    
    if not INSTAGRAPI_AVAILABLE:
        return False
    
    ig_client = IGClient()
    ig_client.set_device({
        "app_version": "269.0.0.18.75",
        "android_version": 26,
        "android_release": "8.0.0",
        "dpi": "480dpi",
        "resolution": "1080x1920",
        "manufacturer": "Apple",
        "device": "iPhone14,5",
        "model": "iPhone 14",
        "cpu": "A15 Bionic",
        "version_code": "314665256"
    })
    ig_client.set_user_agent(
        "Instagram 269.0.0.18.75 (iPhone14,5; iOS 18_0; en_IQ; en-IQ; scale=3.00; 1170x2532; 314665256)"
    )
    ig_client.set_locale("en_IQ")
    ig_client.set_timezone_offset(10800)

    account = load_instagram_account()
    if account.get('username') and account.get('password'):
        session_file = 'Bot/database/instagram_session.json'
        
        if os.path.exists(session_file):
            try:
                ig_client.load_settings(session_file)
                ig_client.login(account['username'], account['password'])
                ig_client.get_timeline_feed()
                last_session_update = datetime.now()
                print("Instagram login with session successful")
                return True
            except Exception as e:
                print(f"Session login failed: {e}, trying fresh login...")
                return force_new_login()
        else:
            return force_new_login()
    return False


def get_ig_client():
    global ig_client, last_session_update
    
    if ig_client is None:
        for attempt in range(MAX_LOGIN_RETRIES):
            if login_instagram():
                break
            print(f"Login attempt {attempt + 1} failed, retrying...")
            time.sleep(2)
    else:
        if last_session_update:
            time_since_update = (datetime.now() - last_session_update).total_seconds()
            if time_since_update > SESSION_UPDATE_INTERVAL:
                if not keep_session_alive():
                    print("Session expired, creating new session...")
                    for attempt in range(MAX_LOGIN_RETRIES):
                        if force_new_login():
                            break
                        print(f"Re-login attempt {attempt + 1} failed...")
                        time.sleep(2)
    
    return ig_client


def extract_username_from_url(url: str) -> str:
    parts = url.split("instagram.com/")[1].split("/")
    if parts[0] == "stories" and len(parts) > 1:
        return parts[1]
    return parts[0].split("?")[0]


async def instagram_fetch(url):
    global ig_client
    
    if not INSTAGRAPI_AVAILABLE:
        return {"success": False, "error": "instagrapi_not_installed"}
    
    max_retries = 2
    
    loop = asyncio.get_event_loop()
    
    def fetch_sync():
        global ig_client
        for attempt in range(max_retries):
            try:
                client = get_ig_client()
                if client is None:
                    return {"success": False, "error": "no_login"}

                result = None
                
                if '/stories/' in url or ('instagram.com/' in url and '/stories' in url):
                    username = extract_username_from_url(url)
                    user_id = client.user_id_from_username(username)
                    stories = client.user_stories(user_id)
                    if not stories:
                        return {"success": False, "error": "no_stories"}
                    story = stories[0]
                    if story.media_type == 2:
                        result = {
                            "success": True,
                            "video_url": str(story.video_url),
                            "username": username,
                            "title": "Instagram Story",
                        }
                    else:
                        return {"success": False, "error": "not_video"}

                elif '/p/' in url or '/reel/' in url or '/tv/' in url:
                    media_pk = client.media_pk_from_url(url)
                    media = client.media_info(media_pk)
                    if media.media_type == 2:
                        result = {
                            "success": True,
                            "video_url": str(media.video_url),
                            "username": media.user.username,
                            "title": media.caption_text if media.caption_text else "Instagram Video",
                        }
                    elif media.media_type == 8:
                        for resource in media.resources:
                            if resource.media_type == 2:
                                result = {
                                    "success": True,
                                    "video_url": str(resource.video_url),
                                    "username": media.user.username,
                                    "title": media.caption_text[:100] if media.caption_text else "Instagram Video",
                                }
                                break
                        if not result:
                            return {"success": False, "error": "no_video_in_album"}
                    else:
                        return {"success": False, "error": "not_video"}

                elif 'instagram.com/' in url and not any(x in url for x in ['/p/', '/reel/', '/tv/', '/stories/']):
                    username = extract_username_from_url(url)
                    user_id = client.user_id_from_username(username)
                    stories = client.user_stories(user_id)
                    if not stories:
                        return {"success": False, "error": "no_stories"}
                    story = stories[0]
                    if story.media_type == 2:
                        result = {
                            "success": True,
                            "video_url": str(story.video_url),
                            "username": username,
                            "title": "Instagram Story",
                        }
                    else:
                        return {"success": False, "error": "not_video"}
                else:
                    return {"success": False, "error": "invalid_url"}
                
                if result:
                    save_session()
                    return result

            except Exception as e:
                error_str = str(e).lower()
                if "login" in error_str or "unauthorized" in error_str or "401" in error_str:
                    print(f"Session error detected: {e}, creating fresh session...")
                    ig_client = None
                    if attempt < max_retries - 1:
                        force_new_login()
                        continue
                    return {"success": False, "error": "login_required"}
                elif "challenge" in error_str:
                    print(f"Challenge required: {e}")
                    save_session()
                    return {"success": False, "error": "challenge_required"}
                else:
                    print(f"Instagram error: {e}")
                    if attempt < max_retries - 1:
                        ig_client = None
                        force_new_login()
                        continue
                    return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "max_retries_exceeded"}
    
    return await loop.run_in_executor(None, fetch_sync)


async def download_file_async(url, output_path, chunk_size=131072):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=300)) as response:
                response.raise_for_status()
                async with aiofiles.open(output_path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(chunk_size):
                        await f.write(chunk)
        return True
    except Exception:
        return False


@Client.on_callback_query(filters.regex(r"^(instagram)$"))
async def instagram_send(client: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    account = load_instagram_account()

    if not account.get('username') or not account.get('password'):
        await callback.message.reply_text(
            "لم يتم إضافة حساب Instagram.\n\n"
            "أضف اسم المستخدم وكلمة المرور في:\n"
            "`Bot/database/instagram_cookies.json`\n\n"
            "{\n"
            '  "username": "your_username",\n'
            '  "password": "your_password"\n'
            "}\n\n"
            "يفضل استخدام حساب ثانوي."
        )
        return

    caption = "يمكنك ارسال الرابط الآن."
    answer = await callback.message.chat.ask(text=caption)
    
    try:
        await client.delete_messages(callback.message.chat.id, answer.id)
    except:
        pass
    
    processing_msg = await callback.message.reply_text("جاري المعالجة...")
    url = answer.text

    response = await instagram_fetch(url)
    if not response["success"]:
        await processing_msg.delete()
        error = response.get("error", "unknown")
        error_messages = {
            "no_login": "لم يتم تسجيل الدخول إلى Instagram.",
            "login_required": "انتهت جلسة Instagram.",
            "challenge_required": "Instagram يطلب تأكيد الحساب.",
            "not_video": "هذا المحتوى ليس فيديو.",
            "no_video_in_album": "لا يوجد فيديو في هذا الألبوم.",
            "no_stories": "لا توجد ستوريات حالياً لهذا الحساب.",
            "invalid_url": "الرابط غير صالح.",
            "instagrapi_not_installed": "مكتبة Instagram غير مثبتة."
        }
        await callback.message.reply_text(error_messages.get(error, f"حدث خطأ: {error}"))
        return

    instagram_user_data[user_id] = response
    video_url = response["video_url"]
    username = response["username"]

    os.makedirs("Bot/downloads", exist_ok=True)
    video_file = f"Bot/downloads/ig_{user_id}_{int(time.time())}.mp4"

    try:
        success = await download_file_async(video_url, video_file)
        if not success:
            await processing_msg.delete()
            await callback.message.reply_text("حدث خطأ في التحميل.")
            return

        bot = await client.get_me()
        bot_name = bot.first_name
        bot_url = f"{bot.username}.t.me"
        caption = f"author : [{username}](https://www.instagram.com/{username})\n\nUploaded By : [{bot_name}]({bot_url})"

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("تحميل بدقه HD", callback_data=f"download_ig_hd_{user_id}"),
                InlineKeyboardButton("ملف صوتي", callback_data=f"download_ig_audio_{user_id}")
            ]
        ])

        await callback.message.reply_video(
            video=video_file,
            caption=caption,
            reply_markup=keyboard
        )

        if os.path.exists(video_file):
            os.remove(video_file)

    except Exception as e:
        print(f"Download error: {e}")
        await callback.message.reply_text("حدث خطأ في التحميل.")

    await processing_msg.delete()


@Client.on_callback_query(filters.regex(r"^download_ig_hd_(\d+)$"))
async def instagram_download_hd(client: Client, callback: CallbackQuery):
    user_id = int(callback.data.split("_")[3])
    if user_id not in instagram_user_data:
        await callback.answer("انتهت صلاحية البيانات", show_alert=True)
        return

    await callback.answer("جاري بدء التحميل...")
    
    data = instagram_user_data[user_id]
    processing_msg = await callback.message.reply_text("جاري تحميل الفيديو بدقة HD...")

    try:
        username = data['username']
        output_file = f"Bot/downloads/ig_hd_{user_id}_{int(time.time())}.mp4"
        
        success = await download_file_async(data['video_url'], output_file)
        if not success:
            await processing_msg.delete()
            await callback.answer("حدث خطأ في التحميل.", show_alert=True)
            return

        bot = await client.get_me()
        bot_name = bot.first_name
        bot_url = f"{bot.username}.t.me"
        caption = f"author : [{username}](https://www.instagram.com/{username})\n\nUploaded By : [{bot_name}]({bot_url})"

        await callback.message.reply_video(video=output_file, caption=caption)

        if os.path.exists(output_file):
            os.remove(output_file)

        await processing_msg.delete()

    except Exception:
        await processing_msg.delete()
        await callback.answer("حدث خطأ في التحميل.", show_alert=True)


@Client.on_callback_query(filters.regex(r"^download_ig_audio_(\d+)$"))
async def instagram_download_audio(client: Client, callback: CallbackQuery):
    user_id = int(callback.data.split("_")[3])
    if user_id not in instagram_user_data:
        await callback.answer("انتهت صلاحية البيانات", show_alert=True)
        return

    await callback.answer("جاري بدء التحميل...")
    
    data = instagram_user_data[user_id]
    processing_msg = await callback.message.reply_text("جاري تحميل الملف الصوتي...")

    try:
        username = data['username']
        title = data['title']
        timestamp = int(time.time())
        output_file = f"Bot/downloads/ig_audio_{user_id}_{timestamp}.mp3"
        video_temp = f"Bot/downloads/ig_temp_{user_id}_{timestamp}.mp4"

        success = await download_file_async(data['video_url'], video_temp)
        if not success:
            await processing_msg.delete()
            await callback.answer("حدث خطأ في التحميل.", show_alert=True)
            return

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: subprocess.run(
                ['ffmpeg', '-i', video_temp, '-vn', '-acodec', 'libmp3lame', '-y', output_file],
                check=True,
                capture_output=True
            )
        )

        bot = await client.get_me()
        bot_name = bot.first_name
        bot_url = f"{bot.username}.t.me"
        caption = f"author : [{username}](https://www.instagram.com/{username})\n\nUploaded By : [{bot_name}]({bot_url})"

        await callback.message.reply_audio(audio=output_file, caption=caption, title=title)

        if os.path.exists(output_file):
            os.remove(output_file)
        if os.path.exists(video_temp):
            os.remove(video_temp)

        await processing_msg.delete()

    except Exception as e:
        print(f"Audio extraction error: {e}")
        await processing_msg.delete()
        await callback.answer("حدث خطأ في التحميل.", show_alert=True)
