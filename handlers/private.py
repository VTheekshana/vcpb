from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton


@Client.on_message(filters.command("start") & filters.private)
async def start(_, message: Message):
     await message.reply_text("**Hi Thereππ» I'am Group Music Player Made By @ImTheekshana**")

@Client.on_message(filters.command("start") & ~filters.private & ~filters.channel)
async def gstart(_, message: Message):
      await message.reply_text("""**π΄ Group Music Player Online.**""",
      reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "π  Source Code π ", url="https://github.com/VTheekshana/vcpb")
                ]
            ]
        )
   )


