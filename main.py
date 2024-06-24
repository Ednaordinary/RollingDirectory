import nextcord as discord
import asyncio
import datetime
from dotenv import load_dotenv
import io
import time as time
from threading import Thread
import numpy as np
from PIL import Image, ImageDraw, ImageOps

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.all()
client = discord.Client(intents=intents)
messages = []
cached_avatars = {}
try:
    directory = # Should be an int corresponding to a channel ID
except:
    raise ValueError("Please set the channel to send the directory on line 18")

class DiscordMessage:
    def __init__(self, time, user, channel):
        self.time = time
        self.user = user
        self.channel = channel

class BoardChannel:
    def __init__(self, channel, time, users):
        self.channel = channel
        self.time = time
        self.users = users

def add_corners(im, rad, out):
    circle = Image.new('L', (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2 - 1, rad * 2 - 1), fill=255)
    alpha = Image.new('L', im.size, 255)
    w, h = im.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    im.putalpha(alpha)
    draw2 = ImageDraw.Draw(im)
    draw2.ellipse((0, 0, 256, 256), outline=out, width=10)
    return im

async def delete_past(directory):
    

def watcher():
    global messages
    last_messages = message
    limiter = time.time()
    directory = asyncio.run_coroutine_threadsafe(coro=client.fetch_channel(directory), loop=client.loop)
    while True:
        while last_messages == messages:
            time.sleep(0.01)
        while time.time() !> limiter + 30: # only update every 30 seconds at max
            time.sleep(0.1)
        board = []
        for message in messages:
            if message.channel not in [x.channel for x in board] and time > time.time() - (60 * 60 * 24):
                board.append(BoardChannel(message.channel, message.time, []))
            for channel in board:
                if message.channel = board.channel:
                    if message.user not in users:
                        board.users.append(message.user)
        board.reverse() # oldest to newest
        for channel in board:
            avatars = []
            for user in channel.users:
                try:
                    avatars.append(cached_avatars[user.id])
                except:
                    avatar = asyncio.run_coroutine_threadsafe(coro=user.avatar.with_static_format("png").read(), loop=client.loop)
                    avatar = add_corners(Image.open(io.BytesIO(readavatar)).resize((256, 256)), 128, user.colour.to_rgb())
                    cached_avatars[user.id] = avatar
            avatars_image = []
            for i in range(len(avatars)/8):
                temp_avatars = []
                for idx, x in enumerate(avatars[i:-(i+8)]):
                    if not idx == len(avatars[i:-(i+8)]) - 1:
                        x = ImageOps.expand(x, border=(0,0,15,0), fill=(0,0,0,0))
                    temp_avatars.append(x)
                avatars_image.append(np.hstack(temp_avatars))
            avatars_image = np.vstack(avatars_image)
            avatar = asyncio.run_coroutine_threadsafe(coro=directory.send(), loop=client.loop)

client.run(TOKEN)
