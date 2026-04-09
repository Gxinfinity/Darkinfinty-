import asyncio
from datetime import datetime
from pyrogram import filters
from pyrogram.enums import ChatType

import config
from Oneforall import app
from Oneforall.core.call import Hotty, autoend
from Oneforall.utils.database import get_client, is_active_chat, is_autoend


# ================== GLOBAL SWITCH ==================
AUTO_LEAVE_ENABLED = False


# ================== COMMAND ==================
@app.on_message(filters.command("autoleave") & filters.user(config.SUDO_USERS))
async def set_autoleave(client, message):
    global AUTO_LEAVE_ENABLED

    if len(message.command) < 2:
        return await message.reply_text(
            "✨ Usage:\n`/autoleave enable` or `/autoleave disable`"
        )

    query = message.command[1].lower()

    if query == "enable":
        AUTO_LEAVE_ENABLED = True
        await message.reply_text("✅ Auto-leave globally enabled.")
    elif query == "disable":
        AUTO_LEAVE_ENABLED = False
        await message.reply_text("❌ Auto-leave globally disabled.")
    else:
        await message.reply_text("❗ Use only `enable` or `disable`.")


# ================== AUTO LEAVE ==================
async def auto_leave():
    await asyncio.sleep(10)

    while True:
        try:
            await asyncio.sleep(900)

            # 🔥 GLOBAL CHECK
            if not AUTO_LEAVE_ENABLED:
                continue

            from Oneforall.core.userbot import assistants

            for num in assistants:
                client = await get_client(num)
                left = 0
                visited = set()

                async for dialog in client.get_dialogs():
                    chat = dialog.chat

                    if chat.id in visited:
                        continue
                    visited.add(chat.id)

                    if chat.type not in [
                        ChatType.SUPERGROUP,
                        ChatType.GROUP,
                        ChatType.CHANNEL,
                    ]:
                        continue

                    if chat.id in [config.LOGGER_ID, -1003809966719]:
                        continue

                    if left >= 20:
                        break

                    try:
                        if not await is_active_chat(chat.id):
                            await client.leave_chat(chat.id)
                            left += 1
                            await asyncio.sleep(1)
                    except:
                        continue

        except Exception as e:
            print(f"[AUTO_LEAVE ERROR]: {e}")


# ================== AUTO END ==================
async def auto_end():
    await asyncio.sleep(10)

    while True:
        try:
            await asyncio.sleep(5)

            if not await is_autoend():
                continue

            for chat_id in list(autoend.keys()):
                timer = autoend.get(chat_id)

                if not timer:
                    continue

                if datetime.now() > timer:
                    autoend[chat_id] = {}

                    try:
                        if await is_active_chat(chat_id):
                            await Hotty.stop_stream(chat_id)
                    except:
                        pass

                    try:
                        await app.send_message(
                            chat_id,
                            "» ʙᴏᴛ ᴀᴜᴛᴏ ʟᴇғᴛ ᴠᴄ ʙᴇᴄᴀᴜsᴇ ɴᴏ ʟɪsᴛᴇɴᴇʀs.",
                        )
                    except:
                        pass

        except Exception as e:
            print(f"[AUTO_END ERROR]: {e}")


# ================== START TASKS ==================
async def start_tasks():
    asyncio.create_task(auto_leave())
    asyncio.create_task(auto_end())


@app.on_message(filters.command("start"))
async def starter(_, __):
    await start_tasks()