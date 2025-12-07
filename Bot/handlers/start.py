from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup as Keyboard, InlineKeyboardButton as Button 
from Bot.funcs import read, write
import pyrogram

users_db = "Bot/database/users.json"
channels_db = "Bot/database/channels.json"
banned_db = "Bot/database/banned.json"
others_db = "Bot/database/others.json"
admins_db = "Bot/database/admins.json"

async def subscription(client, user_id):
    channels = read(channels_db)
    for channel in channels:
        if len(list(channels)) == 0:
            return
        try:
            await client.get_chat_member(chat_id=channel, user_id=user_id)
        except pyrogram.errors.exceptions.bad_request_400.UserNotParticipant:
            return {
                "channel" : channel,
            }
        return False

@Client.on_message(filters.command("start") & filters.private)
async def start(client: Client, message: Message):
    others = read(others_db)
    users = read(users_db)
    admins = read(admins_db)
    user_id = message.from_user.id
    banned = read(banned_db)
    if user_id in banned:
        await message.reply_text(
            "تم حظرك من استخدام البوت تواصل مع المطور ليرفع عنك الحظر."
        )
        return
    if user_id not in users:
        users.append(user_id)
        write(users_db, users)
        if others.get("options")["new_members_notice"]:
            for admin in admins:
                caption: str = f"-> عضو جديد استخدم البوت 🔥\n\n-> ايدي : {user_id}\n-> يوزر : @{message.from_user.username}\n\n-> عدد الأعضاء الحاليين : {len(users)}"
                try:
                    await client.send_message(
                        int(admin),
                        caption
                    )
                except pyrogram.errors.exceptions:
                    continue
    subscribe = await subscription(client ,user_id)
    if subscribe:
        await message.reply_text(
            f"عذرا عزيزي\nعليك الإشتراك بقناة البوت أولا لتتمكن من استخدامه\n{subscribe['channel']}\nاشترك ثم ارسل : /start"
        )
        return
    await message.reply_photo(
        photo="https://k.top4top.io/p_3599c2fl90.jpeg",
        caption="مرحبا بك في بوت التحميل الميديا.\nيمكنك اختيار الموقع الذي تريد من الأزرار في الأسفل :",
        reply_markup=Keyboard([
            [
               Button("- Instagram -", callback_data="instagram"),
               Button("- YouTube -", callback_data="youtube")
            ],
            [
                Button("- Pintrest -", callback_data="pintrest"),
                Button("- Snapchat -", callback_data="snapchat")
            ],
            [
                Button("- TikTok -", callback_data="tiktok"),
                Button("- SoundCloud -", callback_data="soundcloud")
            ],
            [
                Button("- المطور -", url="b01_l.t.me")
            ]
        ])
    )


@Client.on_message(filters.command("المطور", "") & filters.private)
async def dev(client: Client, message: Message):
    chat_id = 2139033978
    user = await client.get_chat(chat_id)
    user_bio = user.bio 
    nickname = user.first_name
    username = user.username
    file_name = f"{user.photo.big_file_id}.jpg"
    photo_path = await client.download_media(user.photo.big_file_id, file_name=file_name)
    caption = f"️\n● NickName: {nickname}\n\n● Username : @{username}\n\n● Bio : {user_bio}\n\n● ID : {chat_id}"
    markup = Keyboard([
        [
            Button(nickname, url=f"{username}.t.me")
        ]
    ])
    await message.reply_photo(photo_path, caption=caption, reply_markup=markup)