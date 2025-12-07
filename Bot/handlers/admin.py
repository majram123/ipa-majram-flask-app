from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup as Keyboard, InlineKeyboardButton as Button 
from Bot.funcs import read, write
import pyrogram, os
import asyncio

users_db = "Bot/database/users.json"
channels_db = "Bot/database/channels.json"
banned_db = "Bot/database/banned.json"
admins_db = "Bot/database/admins.json"
others_db = "Bot/database/others.json"

def keyboard():
    others = read(others_db)
    forward_text = "⎊ التوجيه من الأعضاء ✅" if others["options"]["forward_from_users"] else "⎊ التوجيه من الأعضاء ❌"
    notice_text = "⎊ تنبيه الأعضاء الجدد ✅" if others["options"]["new_members_notice"] else "⎊ تنبيه الأعضاء الجدد ❌"
    
    keys = [
        [
            Button(forward_text, callback_data="forward_from_users"),
            Button(notice_text, callback_data="new_members_notice")
        ],
        [
            Button("⎊ إضافة قناة", callback_data="add_channel"),
            Button("⎊ عرض القنوات", callback_data="current_channels")
        ],
        [
            Button("⎊ حذف قناة", callback_data="remove_channel"),
            Button("⎊ التخزين", callback_data="send_storage")
        ],
        [
            Button("⎊ إذاعة للمستخدمين", callback_data="broadcast")
        ]
    ]
    return keys

@Client.on_message(filters.command("admin") & filters.private)
async def admin(client: Client, message: Message):
    users = read(users_db)
    admins = read(admins_db)
    banned = read(banned_db)
    
    user_id = message.from_user.id
    if user_id not in admins:
        await message.reply_text("هذا الأمر يخص المشرفين")
        return 
    
    markup = Keyboard(keyboard())
    info = await client.get_chat(user_id)
    admin_name = info.first_name
    
    caption = f"""مرحباً ياحلو 🌸 ({admin_name})

الإحصائيات:
• الأعضاء: {len(users)}
• المحظورين: {len(banned)}

الأوامر المتاحة:
• حظر + الأيدي
• رفع حظر + الأيدي  
• رفع ادمن + الأيدي
• تنزيل ادمن + الأيدي"""

    await message.reply_photo(
        photo="https://d.top4top.io/p_35995zl0z0.jpg",
        caption=caption,
        reply_markup=markup
    )


@Client.on_callback_query(filters.regex(r"^(broadcast)$"))
async def broadcast_handler(client: Client, callback: CallbackQuery):
    admins = read(admins_db)
    user_id = callback.from_user.id
    if user_id not in admins:
        await callback.answer("هذا الأمر يخص المشرفين", show_alert=True)
        return
    
    await callback.message.edit_text("⎊ أرسل الآن الرسالة التي تريد إذاعتها لجميع الأعضاء:\n⎊ يمكنك إرسال (نص، صورة، فيديو، ملصق، إلخ)")
    
    try:
        response = await client.listen(callback.message.chat.id, timeout=300)
        
        # حفظ بيانات الرسالة بشكل صحيح
        broadcast_data = {
            "message_type": "text" if response.text else "media",
            "content": response.text if response.text else "",
            "media_file_id": None,
            "caption": response.caption if hasattr(response, 'caption') and response.caption else ""
        }
        
        # حفظ معرف الملف للوسائط
        if response.photo:
            broadcast_data["media_file_id"] = response.photo.file_id
            broadcast_data["message_type"] = "photo"
        elif response.video:
            broadcast_data["media_file_id"] = response.video.file_id
            broadcast_data["message_type"] = "video"
        elif response.document:
            broadcast_data["media_file_id"] = response.document.file_id
            broadcast_data["message_type"] = "document"
        elif response.audio:
            broadcast_data["media_file_id"] = response.audio.file_id
            broadcast_data["message_type"] = "audio"
        elif response.voice:
            broadcast_data["media_file_id"] = response.voice.file_id
            broadcast_data["message_type"] = "voice"
        elif response.sticker:
            broadcast_data["media_file_id"] = response.sticker.file_id
            broadcast_data["message_type"] = "sticker"
        
        # حفظ البيانات المؤقتة
        others = read(others_db)
        others["temp_broadcast"] = broadcast_data
        write(others_db, others)
        
        confirm_markup = Keyboard([
            [Button("⎊ تأكيد الإذاعة", callback_data="confirm_broadcast")],
            [Button("⎊ إلغاء الإذاعة", callback_data="cancel_broadcast")]
        ])
        
        # عرض معاينة الرسالة
        if response.text:
            await response.reply_text(
                f"⎊ هذه هي الرسالة التي تريد إذاعتها:\n\n{response.text}\n\n⎊ اضغط على تأكيد الإذاعة للمتابعة",
                reply_markup=confirm_markup
            )
        else:
            await response.copy(
                chat_id=callback.message.chat.id,
                caption="⎊ هذه هي الرسالة التي تريد إذاعتها:\n⎊ اضغط على تأكيد الإذاعة للمتابعة" + (f"\n⎊ التسمية: {response.caption}" if hasattr(response, 'caption') and response.caption else ""),
                reply_markup=confirm_markup
            )
        
    except asyncio.TimeoutError:
        await callback.message.edit_text("⎊ تم إلغاء الإذاعة بسبب انتهاء الوقت")


@Client.on_callback_query(filters.regex(r"^(confirm_broadcast)$"))
async def confirm_broadcast(client: Client, callback: CallbackQuery):
    users = read(users_db)
    banned = read(banned_db)
    others = read(others_db)
    user_id = callback.from_user.id
    admins = read(admins_db)
    
    if user_id not in admins:
        await callback.answer("هذا الأمر يخص المشرفين", show_alert=True)
        return
    
    broadcast_data = others.get("temp_broadcast", {})
    if not broadcast_data:
        await callback.message.edit_text("⎊ لم يتم العثور على بيانات الإذاعة")
        return
    
    # بدء الإذاعة
    progress_msg = await callback.message.edit_text("⎊ جاري بدء الإذاعة للأعضاء...\n⎊ التقدم: 0%")
    
    success_count = 0
    fail_count = 0
    total_users = len(users)
    
    # إرسال الرسالة لكل مستخدم
    for index, user_id in enumerate(users):
        if user_id in banned:  # تخطي المحظورين
            continue
            
        try:
            if broadcast_data["message_type"] == "text":
                await client.send_message(
                    chat_id=user_id,
                    text=broadcast_data["content"]
                )
            else:
                # إرسال الوسائط بناءً على النوع
                media_type = broadcast_data["message_type"]
                file_id = broadcast_data["media_file_id"]
                caption = broadcast_data.get("caption", "")
                
                if media_type == "photo":
                    await client.send_photo(
                        chat_id=user_id,
                        photo=file_id,
                        caption=caption
                    )
                elif media_type == "video":
                    await client.send_video(
                        chat_id=user_id,
                        video=file_id,
                        caption=caption
                    )
                elif media_type == "document":
                    await client.send_document(
                        chat_id=user_id,
                        document=file_id,
                        caption=caption
                    )
                elif media_type == "audio":
                    await client.send_audio(
                        chat_id=user_id,
                        audio=file_id,
                        caption=caption
                    )
                elif media_type == "voice":
                    await client.send_voice(
                        chat_id=user_id,
                        voice=file_id,
                        caption=caption
                    )
                elif media_type == "sticker":
                    await client.send_sticker(
                        chat_id=user_id,
                        sticker=file_id
                    )
            
            success_count += 1
            
            # تحديث التقدم كل 50 مستخدم
            if index % 50 == 0:
                progress = int((index / total_users) * 100)
                await progress_msg.edit_text(f"⎊ جاري بدء الإذاعة للأعضاء...\n⎊ التقدم: {progress}%")
            
            await asyncio.sleep(0.1)  # تجنب التقييد
            
        except Exception as e:
            print(f"Failed to send to {user_id}: {e}")
            fail_count += 1
    
    # عرض نتائج الإذاعة
    result_text = f"""
⎊ تم الانتهاء من الإذاعة بنجاح ✅

⎊ الإحصائيات:
• عدد الأعضاء المستهدفين: {total_users}
• عدد الرسائل المرسلة: {success_count}
• عدد الرسائل الفاشلة: {fail_count}
• نسبة النجاح: {round((success_count/total_users)*100, 2) if total_users > 0 else 0}%
"""
    
    # تنظيف البيانات المؤقتة
    if "temp_broadcast" in others:
        del others["temp_broadcast"]
        write(others_db, others)
    
    await progress_msg.edit_text(result_text)


@Client.on_callback_query(filters.regex(r"^(cancel_broadcast)$"))
async def cancel_broadcast(client: Client, callback: CallbackQuery):
    # تنظيف البيانات المؤقتة
    others = read(others_db)
    if "temp_broadcast" in others:
        del others["temp_broadcast"]
        write(others_db, others)
    
    await callback.message.edit_text("⎊ تم إلغاء الإذاعة")


# باقي الدوال كما هي...
@Client.on_message(filters.regex(r"^(حظر)") & filters.private)
async def ban(client: Client, message: Message):
    admins = read(admins_db)
    banned = read(banned_db)
    
    user_id = message.from_user.id
    if user_id not in admins:
        await message.reply_text("هذا الأمر يخص المشرفين")
        return
    
    member = message.text.split()[-1]
    if not member.isdigit():
        await message.reply_text("يرجى إدخال أيدي مستخدم صحيح")
        return
        
    member = int(member)
    
    if member in admins:
        await message.reply_text("لا يمكنك حظر هذا المستخدم")
        return
        
    if member in banned:
        await message.reply_text("تم حظر هذا المستخدم من قبل")
        return
        
    banned.append(member)
    write(banned_db, banned)
    await message.reply_text("تم حظر هذا المستخدم")

@Client.on_message(filters.regex(r"^(رفع حظر)") & filters.private)
async def unban(client: Client, message: Message):
    admins = read(admins_db)
    banned = read(banned_db)
    
    user_id = message.from_user.id
    if user_id not in admins:
        await message.reply_text("هذا الأمر يخص المشرفين")
        return
    
    member = message.text.split()[-1]
    if not member.isdigit():
        await message.reply_text("يرجى إدخال أيدي مستخدم صحيح")
        return
        
    member = int(member)
    
    if member in banned:
        banned.remove(member)
        write(banned_db, banned)
        await message.reply_text("تم رفع الحظر عن هذا المستخدم")
    else:
        await message.reply_text("لم يتم حظر هذا المستخدم من قبل")
    

@Client.on_message(filters.regex(r"^(رفع ادمن)") & filters.private)
async def promote_admin(client: Client, message: Message):
    admins = read(admins_db)
    banned = read(banned_db)
    
    user_id = message.from_user.id
    if user_id not in admins:
        await message.reply_text("هذا الأمر يخص المشرفين")
        return
    
    member = message.text.split()[-1]
    if not member.isdigit():
        await message.reply_text("يرجى إدخال أيدي مستخدم صحيح")
        return
        
    member = int(member)
    
    if member in admins:
        await message.reply_text("هذا المستخدم مشرف بالفعل")
        return
        
    if member in banned:
        await message.reply_text("هذا المستخدم محظور يرجى رفع الحظر ثم إعادة المحاولة")
        return
        
    admins.append(member)
    write(admins_db, admins)
    await message.reply_text("تم ترقية المستخدم لرتبة مشرف")
    
    
@Client.on_message(filters.regex(r"^(تنزيل ادمن)") & filters.private)
async def demote_admin(client: Client, message: Message):
    admins = read(admins_db)
    
    user_id = message.from_user.id
    if user_id not in admins:
        await message.reply_text("هذا الأمر يخص المشرفين")
        return
    
    member = message.text.split()[-1]
    if not member.isdigit():
        await message.reply_text("يرجى إدخال أيدي مستخدم صحيح")
        return
        
    member = int(member)
    
    if member in admins:
        admins.remove(member)
        write(admins_db, admins)
        await message.reply_text("تم تنزيل هذا المستخدم من قائمة المشرفين")
    else:
        await message.reply_text("هذا المستخدم ليس من المشرفين")


@Client.on_callback_query(filters.regex(r"^(forward_from_users|new_members_notice)$"))
async def redefine(client: Client, callback: CallbackQuery):
    admins = read(admins_db)
    others = read(others_db)
    
    user_id = callback.from_user.id
    if user_id not in admins:
        await callback.answer("هذا الأمر يخص المشرفين", show_alert=True)
        return
    
    data = callback.data
    others["options"][data] = not others["options"][data]
    write(others_db, others)
    
    await callback.message.edit_reply_markup(
        reply_markup=Keyboard(keyboard())
    )
    
    # إشعار المستخدم بنجاح العملية
    status = "مفعّل ✅" if others["options"][data] else "معطّل ❌"
    option_name = "التوجيه من الأعضاء" if data == "forward_from_users" else "تنبيه الأعضاء الجدد"
    await callback.answer(f"⎊ {option_name} الآن {status}", show_alert=True)


@Client.on_callback_query(filters.regex(r"^(add_channel)$"))
async def add_channel(client: Client, callback: CallbackQuery):
    admins = read(admins_db)
    channels = read(channels_db)
    
    user_id = callback.from_user.id
    if user_id not in admins:
        await callback.answer("هذا الأمر يخص المشرفين", show_alert=True)
        return
        
    await callback.message.edit_text("⎊ أرسل معرف القناة مع البدء ب @")
    
    try:
        response = await client.listen(callback.message.chat.id, timeout=60)
        channel = response.text.strip()
        
        if not channel.startswith("@"):
            await response.reply_text("⎊ يجب أن يبدأ معرف القناة ب @")
            return
        
        try:
            await client.get_chat(channel)
        except pyrogram.errors.exceptions.bad_request_400.UsernameInvalid:
            await response.reply_text("⎊ لم يتم إيجاد هذه الدردشة")
            return
            
        if channel in channels:
            await response.reply_text("⎊ القناة موجودة بالفعل")
            return
            
        channels.append(channel)
        write(channels_db, channels)
        await response.reply_text("⎊ تمت إضافة القناة")
    except asyncio.TimeoutError:
        await callback.message.reply_text("⎊ انتهى الوقت")


@Client.on_callback_query(filters.regex(r"^(remove_channel)$"))
async def remove_channel(client: Client, callback: CallbackQuery):
    admins = read(admins_db)
    channels = read(channels_db)
    
    user_id = callback.from_user.id
    if user_id not in admins:
        await callback.answer("هذا الأمر يخص المشرفين", show_alert=True)
        return
        
    await callback.message.edit_text("⎊ أرسل معرف القناة مع البدء ب @")
    
    try:
        response = await client.listen(callback.message.chat.id, timeout=60)
        channel = response.text.strip()
        
        if not channel.startswith("@"):
            await response.reply_text("⎊ يجب أن يبدأ معرف القناة ب @")
            return
        
        if channel not in channels:
            await response.reply_text("⎊ لم يتم إيجاد هذه القناة")
            return
            
        channels.remove(channel)
        write(channels_db, channels)
        await response.reply_text("⎊ تم حذف القناة")
    except asyncio.TimeoutError:
        await callback.message.reply_text("⎊ انتهى الوقت")


@Client.on_callback_query(filters.regex(r"^(current_channels)$"))
async def current_channels(client: Client, callback: CallbackQuery):
    channels = read(channels_db)
    
    if not channels:
        caption = "⎊ لا توجد قنوات مضافة حالياً"
    else:
        caption = "⎊ القنوات المضافة:\n" + "\n".join([f"• {channel}" for channel in channels])
    
    await client.answer_callback_query(
        callback_query_id=callback.id,
        text=caption, 
        show_alert=True
    )


@Client.on_callback_query(filters.regex(r"^(send_storage)$"))
async def send_storage(client: Client, callback: CallbackQuery):
    admins = read(admins_db)
    
    user_id = callback.from_user.id
    if user_id not in admins:
        await callback.answer("هذا الأمر يخص المشرفين", show_alert=True)
        return
        
    files_path = "Bot/database"
    files = os.listdir(files_path)
    
    for file in files:
        file_path = os.path.join(files_path, file)
        await client.send_document(
            callback.message.chat.id,
            document=file_path
        )