# -*- coding: iso-8859-1 -*-
from datetime import datetime
from os import environ, path
from time import time
from requests import get
from discord.ext import tasks
import discord
import requests
import json

#####################
# Bot Configuration #
#####################
# Setting environment variables is preferred, but you can also edit the variables below.
client = discord.Client(intents=discord.Intents.all())
client = discord.Client(intents=discord.Intents.default())
# Discord (Required)
DCLONE_DISCORD_TOKEN = ('')
DCLONE_DISCORD_CHANNEL_ID = int('')

api_url = "https://d2runewizard.com/api/terror-zone"
response = requests.get(api_url)
headers =  {"Content-Type":"application/json",
            "token": "String",
            "D2R-Contact": "",
            "D2R-Platform": "",
            "D2R-Repo": ""}
response = requests.post(api_url, headers=headers)
response.json()
jsonResponse = response.json()
print(jsonResponse)
response.status_code

########################
# End of configuration #
########################


if __name__ == '__main__':
    client.run(DCLONE_DISCORD_TOKEN)
