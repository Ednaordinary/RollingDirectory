import nextcord as discord
import asyncio
import datetime
from dotenv import load_dotenv
import io
import os
import math
import time as time
from threading import Thread
import requests
import numpy as np
from PIL import Image, ImageDraw, ImageOps

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.all()
client = discord.Client(intents=intents)
messages = []
cached_avatars = {}
directory = # Should be an int corresponding to a channel I

class DiscordMessage:
    def __init__(self, time, user, channel, message_id):
        self.time = time
        self.user = user
        self.channel = channel
        self.message_id = message_id

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
    async for message in directory.history(limit=None, before=datetime.datetime.fromtimestamp(time.time()), oldest_first=True):
        await message.delete()

def watcher():
    global messages
    global directory
    last_messages = [x for x in messages]
    limiter = time.time() - 30
    directory = asyncio.run_coroutine_threadsafe(coro=client.fetch_channel(directory), loop=client.loop).result()
    while True:
        while last_messages == messages:
            time.sleep(0.01)
        while time.time() <= limiter + 30: # only update every 30 seconds at max
            time.sleep(0.1)
            print("sleeping for limiter")
        board = []
        asyncio.run_coroutine_threadsafe(coro=delete_past(directory), loop=client.loop)
        for message in messages:
            if message.channel not in [x.channel for x in board] and message.time > time.time() - (60 * 60 * 24):
                board.append(BoardChannel(channel=message.channel, time=message.time, users=[]))
            for channel in board:
                if message.channel.id == channel.channel.id:
                    if message.user not in channel.users:
                        channel.users.append(message.user)
        board.reverse() # oldest to newest
        for channel in board:
            avatars = []
            for user in channel.users:
                try:
                    avatars.append(cached_avatars[user.id])
                except:
                    avatar = requests.get(user.display_avatar.url).content
                    avatar = add_corners(Image.open(io.BytesIO(avatar)).resize((256, 256)), 128, user.colour.to_rgb())
                    cached_avatars[user.id] = avatar
            avatars_image = []
            for i in range(int(math.ceil(len(avatars)/8))):
                temp_avatars = []
                for idx, x in enumerate(avatars[i:-(i+8)]):
                    if not idx == len(avatars[i:-(i+8)]) - 1:
                        x = ImageOps.expand(x, border=(0,0,15,0), fill=(0,0,0,0))
                    temp_avatars.append(x)
                avatars_image.append(np.hstack(temp_avatars))
            try:
                avatars_image = np.vstack(avatars_image)
            except:
                avatars_image = None
            asyncio.run_coroutine_threadsafe(coro=directory.send("# " + channel.channel.name + " <t:" + channel.time + ":R>", file=discord.File(fp=io.BytesIO(avatars_image), filename='avatars.png')), loop=client.loop)
        last_message = messages
        limiter = time.time()

@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')

@client.event
async def on_message(message):
    global messages
    messages.append(DiscordMessage(time=message.created_at.timestamp(), user=message.author, channel=message.channel, message_id=message.id))
    print("added message")

@client.event
async def on_raw_message_delete(payload):
    global messages
    for idx, message in enumerate(messages):
        if message.message_id == message.id:
            messages.pop(idx)
            break

Thread(target=watcher).start()
client.run(TOKEN)
