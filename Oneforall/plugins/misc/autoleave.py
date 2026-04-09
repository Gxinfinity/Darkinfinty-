import asyncio
from datetime import datetime
from pyrogram import filters
from pyrogram.enums import ChatType

import config
from Oneforall import app
from Oneforall.core.call import Hotty, autoend
from Oneforall.utils.database import get_client, is_active_chat, is_autoend

# --- Sudoers/Owner Command to Toggle ---
# Yahan SUDOERS ko badal kar config.SUDO_USERS kar diya hai
@app.on_message(filters.command("autoleave") & filters.user(config.SUDO_USERS))
async def set_autoleave(client, message):
    if len(message.command) < 2:
        return await message.reply_text("✨ **Usage:**\n`/autoleave [on|off]`")

    query = message.text.split(None, 1)[1].lower()
    if query == "on":
        config.AUTO_LEAVING_ASSISTANT = True
        await message.reply_text("✅ **Auto-leave enabled.** Assistant will leave inactive chats every 15 mins.")
    elif query == "off":
        config.AUTO_LEAVING_ASSISTANT = False
        await message.reply_text("❌ **Auto-leave disabled.**")
    else:
        await message.reply_text("Invalid option! Use `on` or `off`.")

# --- Fixed Auto Leave Logic ---
async def auto_leave():
    while True:
        await asyncio.sleep(900) # Har 15 minute mein check karega

        # Check if enabled in config
        if config.AUTO_LEAVING_ASSISTANT:
            from Oneforall.core.userbot import assistants

            for num in assistants:
                client = await get_client(num)
                left = 0
                try:
                    async for i in client.get_dialogs():
                        if i.chat.type in [ChatType.SUPERGROUP, ChatType.GROUP, ChatType.CHANNEL]:
                            # Exclude Logger and specific IDs
                            if i.chat.id != config.LOGGER_ID and i.chat.id != -1003809966719:
                                if left == 20: # Spam prevention
                                    break

                                if not await is_active_chat(i.chat.id):
                                    try:
                                        await client.leave_chat(i.chat.id)
                                        left += 1
                                    except:
                                        continue
                except Exception:
                    pass

# --- Auto End Logic ---
async def auto_end():
    while True:
        await asyncio.sleep(5)
        ender = await is_autoend()
        if not ender:
            continue
        for chat_id in list(autoend): 
            timer = autoend.get(chat_id)
            if not timer:
                continue
            if datetime.now() > timer:
                if not await is_active_chat(chat_id):
                    autoend[chat_id] = {}
                    continue
                autoend[chat_id] = {}
                try:
                    await Hotty.stop_stream(chat_id)
                except:
                    continue
                try:
                    await app.send_message(
                        chat_id,
                        "» ʙᴏᴛ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ʟᴇғᴛ ᴠɪᴅᴇᴏᴄʜᴀᴛ ʙᴇᴄᴀᴜsᴇ ɴᴏ ᴏɴᴇ ᴡᴀs ʟɪsᴛᴇɴɪɴɢ.",
                    )
                except:
                    continue

# Tasks start karein
asyncio.create_task(auto_leave())
asyncio.create_task(auto_end())
