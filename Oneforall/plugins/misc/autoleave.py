import asyncio
from datetime import datetime
from pyrogram.enums import ChatType

import config
from Oneforall import app
from Oneforall.core.call import Hotty, autoend
from Oneforall.utils.database import get_client, is_active_chat, is_autoend


# ================== AUTO LEAVE ==================
async def auto_leave():
    await asyncio.sleep(15)

    while True:
        try:
            await asyncio.sleep(900)

            # 🔥 HARD GLOBAL CHECK
            if not config.AUTO_LEAVING_ASSISTANT:
                continue

            from Oneforall.core.userbot import assistants

            for num in assistants:
                client = await get_client(num)
                left = 0

                async for i in client.get_dialogs():
                    chat = i.chat

                    if chat.type not in [
                        ChatType.SUPERGROUP,
                        ChatType.GROUP,
                        ChatType.CHANNEL,
                    ]:
                        continue

                    if chat.id in [
                        config.LOGGER_ID,
                        -1001626004802,
                        -1001876397776,
                    ]:
                        continue

                    if left >= 20:
                        break

                    # 🔥 SAFE CHECK
                    try:
                        active = await is_active_chat(chat.id)
                    except:
                        active = True  # safety

                    # ❌ inactive hone pe bhi leave mat kar (safe mode)
                    if not active:
                        continue

                    try:
                        await client.leave_chat(chat.id)
                        left += 1
                        await asyncio.sleep(1)
                    except:
                        continue

        except Exception as e:
            print(f"[AUTO_LEAVE ERROR]: {e}")


# ================== AUTO END ==================
async def auto_end():
    await asyncio.sleep(15)

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


# 🔥 SAFE START (delay ke baad)
async def start_tasks():
    await asyncio.sleep(20)
    asyncio.create_task(auto_leave())
    asyncio.create_task(auto_end())


asyncio.get_event_loop().create_task(start_tasks())