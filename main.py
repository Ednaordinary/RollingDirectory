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
directory = 1124170292508495892 # Should be an int corresponding to a channel

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

def add_corners(im, rad):
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
        board = []
        asyncio.run_coroutine_threadsafe(coro=delete_past(directory), loop=client.loop)
        time.sleep(1) # give bots a second to reply if they are being commanded
        reversed_messages = [x for x in messages]
        reversed_messages.reverse()
        for message in reversed_messages:
            if message.channel not in [x.channel for x in board] and message.time > time.time() - (60 * 60 * 24):
                board.append(BoardChannel(channel=message.channel, time=message.time, users=[]))
            for channel in board:
                if message.channel.id == channel.channel.id:
                    if message.user not in channel.users:
                        channel.users.append(message.user)
        board.reverse() # oldest to newest
        asyncio.run_coroutine_threadsafe(coro=directory.send("**Rolling Directory**\n\nThis is the rolling directory. It follows channels that have had messages in the past 24 hours."), loop=client.loop)
        for channel in board:
            avatars = []
            for user in channel.users:
                try:
                    avatars.append(cached_avatars[user.id])
                except:
                    avatar = requests.get(user.display_avatar.url).content
                    avatar = add_corners(Image.open(io.BytesIO(avatar)).convert('RGB').resize((128, 128)), 64)
                    cached_avatars[user.id] = avatar
                    avatars.append(avatar)
            avatars_image = [[]]
            for idx, i in enumerate(avatars):
                if not idx % 8:
                    avatars_image.append([])
                avatars_image[-1].append(i)
            avatars_vstack = []
            for row in avatars_image:
                temp_avatars = []
                for idx, x in enumerate(row):
                    if idx != len(row) - 1:
                        x = ImageOps.expand(x, border=(0,0,15,0), fill=(0,0,0,0))
                    temp_avatars.append(x)
                if temp_avatars != []:
                    avatars_vstack.append(np.hstack(temp_avatars))
            if avatars_vstack != []:
                avatars_image = ImageOps.pad(Image.fromarray(np.vstack(avatars_vstack)), (1129, 128), color=(0, 0, 0, 0))
                with io.BytesIO() as imagebn:
                    avatars_image.save(imagebn, "PNG")
                    imagebn.seek(0)
                    asyncio.run_coroutine_threadsafe(coro=directory.send("# <#" + str(channel.channel.id) + "> <t:" + str(int(channel.time)) + ":R>", file=discord.File(fp=imagebn, filename='avatars.png')), loop=client.loop)
            else:
                asyncio.run_coroutine_threadsafe(coro=directory.send("# <#" + str(channel.channel.id) + "> <t:" + str(int(channel.time)) + ":R>"), loop=client.loop)
        last_messages = [x for x in messages]
        limiter = time.time()

@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')

@client.event
async def on_message(message):
    global messages
    global directory
    if not message.channel == directory: 
        messages.append(DiscordMessage(time=message.created_at.timestamp(), user=message.author, channel=message.channel, message_id=message.id))

@client.event
async def on_raw_message_delete(payload):
    global messages
    for idx, message in enumerate(messages):
        if message.message_id == payload.message_id:
            messages.pop(idx)
            break

Thread(target=watcher).start()
client.run(TOKEN)
