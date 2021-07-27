from asyncio.queues import QueueEmpty

from pyrogram import Client, filters
from pyrogram.types import Message
from callsmusic import callsmusic

from config import CHAT_ID, SUDO_USERS
from helpers.filters import command, other_filters
from helpers.decorators import errors


@Client.on_message(command("pause") & filters.private & filters.user(SUDO_USERS))
@errors
async def pause(_, message: Message):
    if (
            CHAT_ID not in callsmusic.pytgcalls.active_calls
    ) or (
            callsmusic.pytgcalls.active_calls[CHAT_ID] == 'paused'
    ):
        await message.reply_text("**❗ Nothing is playing!**")
    else:
        callsmusic.pytgcalls.pause_stream(CHAT_ID)
        await message.reply_text("**▶️ Paused!**")


@Client.on_message(command("resume") & filters.private & filters.user(SUDO_USERS))
@errors
async def resume(_, message: Message):
    if (
            CHAT_ID not in callsmusic.pytgcalls.active_calls
    ) or (
            callsmusic.pytgcalls.active_calls[CHAT_ID] == 'playing'
    ):
        await message.reply_text("**❗ Nothing is paused!**")
    else:
        callsmusic.pytgcalls.resume_stream(CHAT_ID)
        await message.reply_text("**⏸ Resumed!**")


@Client.on_message(command("end") & filters.private & filters.user(SUDO_USERS))
@errors
async def stop(_, message: Message):
    if CHAT_ID not in callsmusic.pytgcalls.active_calls:
        await message.reply_text("**❗ Nothing is streaming!**")
    else:
        try:
            callsmusic.queues.clear(CHAT_ID)
        except QueueEmpty:
            pass

        callsmusic.pytgcalls.leave_group_call(CHAT_ID)
        await message.reply_text("**❌ Stopped streaming!**")


@Client.on_message(command("skip") & filters.private & filters.user(SUDO_USERS))
@errors
async def skip(_, message: Message):
    if CHAT_ID not in callsmusic.pytgcalls.active_calls:
        await message.reply_text("**❗ Nothing is playing to skip!**")
    else:
        callsmusic.queues.task_done(CHAT_ID)

        if callsmusic.queues.is_empty(CHAT_ID):
            callsmusic.pytgcalls.leave_group_call(CHAT_ID)
        else:
            callsmusic.pytgcalls.change_stream(
                CHAT_ID,
                callsmusic.queues.get(CHAT_ID)["file"]
            )

        await message.reply_text("**➡️ Skipped the current song!**")
