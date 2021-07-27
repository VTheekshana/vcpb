import os
from os import path
from pyrogram import Client, filters
from pyrogram.types import Message, Voice, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import UserAlreadyParticipant
from callsmusic import callsmusic, queues
from helpers.admins import get_administrators
import requests
import aiohttp
import youtube_dl
from youtube_search import YoutubeSearch
import converter
from downloaders import youtube
from config import DURATION_LIMIT, CHAT_ID
from helpers.filters import command
from helpers.decorators import errors
from helpers.errors import DurationLimitError
from helpers.gets import get_url, get_file_name
import aiofiles
import ffmpeg
from PIL import Image, ImageFont, ImageDraw


def transcode(filename):
    ffmpeg.input(filename).output("input.raw", format='s16le', acodec='pcm_s16le', ac=2, ar='48k').overwrite_output().run() 
    os.remove(filename)

# Convert seconds to mm:ss
def convert_seconds(seconds):
    seconds = seconds % (24 * 3600)
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%02d:%02d" % (minutes, seconds)


# Convert hh:mm:ss to seconds
def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(':'))))


# Change image size
def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage

async def generate_cover(requested_by, title, views, duration, thumbnail):
    async with aiohttp.ClientSession() as session:
        async with session.get(thumbnail) as resp:
            if resp.status == 200:
                f = await aiofiles.open("background.png", mode="wb")
                await f.write(await resp.read())
                await f.close()

    image1 = Image.open("./background.png")
    image2 = Image.open("etc/foreground.png")
    image3 = changeImageSize(1280, 720, image1)
    image4 = changeImageSize(1280, 720, image2)
    image5 = image3.convert("RGBA")
    image6 = image4.convert("RGBA")
    Image.alpha_composite(image5, image6).save("temp.png")
    img = Image.open("temp.png")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("etc/font.otf", 32)
    draw.text((190, 550), f"Title: {title}", (255, 255, 255), font=font)
    draw.text(
        (190, 590), f"Duration: {duration}", (255, 255, 255), font=font
    )
    draw.text((190, 630), f"Views: {views}", (255, 255, 255), font=font)
    draw.text((190, 670),
        f"Added By: {requested_by}",
        (255, 255, 255),
        font=font,
    )
    img.save("final.png")
    os.remove("temp.png")
    os.remove("background.png")




@Client.on_message(filters.text & filters.private)
async def play(client, message: Message):
    input = message.text
    if input.startswith("/"):
       return
    lel = await message.reply("**✅ Download scheduled.**")
    url = input
    try:
         results = YoutubeSearch(url, max_results=1).to_dict()
         # print results
         title = results[0]["title"]       
         thumbnail = results[0]["thumbnails"][0]
         thumb_name = f'thumb{title}.jpg'
         thumb = requests.get(thumbnail, allow_redirects=True)
         open(thumb_name, 'wb').write(thumb.content)
         duration = results[0]["duration"]
         url_suffix = results[0]["url_suffix"]
         views = results[0]["views"]
            
         secmul, dur, dur_arr = 1, 0, duration.split(':')
         for i in range(len(dur_arr)-1, -1, -1):
             dur += (int(dur_arr[i]) * secmul)
             secmul *= 60   
                  
    except:
        return await lel.edit("**❌ Error.**")        
            
    if (dur / 60) > DURATION_LIMIT:
        await lel.edit(f"**❌ Videos longer than {DURATION_LIMIT} minutes aren't allowed to play!**")
        return
    requested_by = message.from_user.first_name
    await generate_cover(requested_by, title, views, duration, thumbnail)     
    file_path = await converter.convert(youtube.download(url))
    
    if CHAT_ID in callsmusic.pytgcalls.active_calls:
        position = await queues.put(CHAT_ID, file=file_path)
        await client.send_photo(
        CHAT_ID,
        photo="final.png", 
        caption="**🎵 Song:** {}\n**🕒 Duration:** {} min\n**👤 Added By:** {}\n\n**#⃣ Queued Position:** {}".format(
        title, duration, message.from_user.mention(), position
        ),
        reply_markup=keyboard)
        os.remove("final.png")
        return await lel.edit(f"**#️⃣ Scheduled to play at position {}**")
    else:
        callsmusic.pytgcalls.join_group_call(CHAT_ID, file_path)
        await client.send_photo(
        CHAT_ID,
        photo="final.png",
        reply_markup=keyboard,
        caption="**🎵 Song:** {}\n**🕒 Duration:** {} min\n**👤 Added By:** {}\n\n**▶️ Now Playing at `{}`...**".format(
        title, duration, message.from_user.mention(), message.chat.title
        ), )
        os.remove("final.png")
        return await lel.edit("**▶️ Playing...**")
