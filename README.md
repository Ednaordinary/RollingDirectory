# RollingDirectory
Rolling Directory for discord

## What is it?
It follows channels that have had messages in the past 24 hours. This makes it easier to navigate the server.

## Run

`git clone https://github.com/Ednaordinary/RollingDirectory/`

`cd RollingDirectory`

`python3 -m venv venv`

`source bin/activate`

`cd ..`

`pip install -r requirements.txt`

Then, put the channel ID for the directory bot in line 18 of main.py

Put your bot token in a .env as DISCORD_TOKEN

The bot should have permissions to delete messages (it needs to delete messages in the rolling directory channel)

`python3 ./main.py`

![image](https://github.com/Ednaordinary/RollingDirectory/assets/88869424/5f76b1d3-de4b-4dcf-9a1e-ae9355240e13)
