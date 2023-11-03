# -*- coding: iso-8859-1 -*-
import logging.handlers
from datetime import datetime
from os import environ, path

from discord.ext import tasks
from requests import get
import discord

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
logging.getLogger('discord.http').setLevel(logging.INFO)

handler = logging.handlers.RotatingFileHandler(
    filename='discord.log',
    encoding='utf-8',
    maxBytes=32 * 1024 * 1024,  # 32 MiB
    backupCount=5,  # Rotate through 5 files
)
dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
handler.setFormatter(formatter)
logger.addHandler(handler)

#####################
# Bot Configuration #
#####################
# Setting environment variables is preferred, but you can also edit the variables below.

# Discord (Required)
TOKEN = ('')
CHANEL = int('')

# D2RuneWizard API (Optional but recommended)
# Token and contact (email address) are necessary for planned walk notifications
D2RW_TOKEN = ('')
D2RW_CONTACT = ('')

########################
# End of configuration #
########################
__version__ = '0.1a'
REGION = {'1': 'Americas', '2': 'Europe', '3': 'Asia', '': 'All Regions'}
LADDER = {'1': 'Ladder', '2': 'Non-Ladder', '': 'Ladder and Non-Ladder'}
LADDER_RW = {True: 'Ladder', False: 'Non-Ladder'}
HC = {'1': 'Hardcore', '2': 'Softcore', '': 'Hardcore and Softcore'}
HC_RW = {True: 'Hardcore', False: 'Softcore'}
dt_hour_last = None
last_update = None

# DCLONE_DISCORD_TOKEN and DCLONE_DISCORD_CHANNEL_ID are required
if not TOKEN or CHANEL == 0:
    print('Please set Discord "TOKEN" and CHANNEL "ID" in your environment.')
    exit(1)

if path.isfile('email.txt'):
    efr = open('email.txt', 'r').read()
else:
    with open('email.txt', 'w') as efr_w:
        efr = input('https://d2runewizard.com needs an email in order to authenticate to its api, please enter one:')
        efr_w.write(efr)
headers = {
    "D2R-Contact": efr.replace('\n', ''),
    "D2R-Platform": "Discord",
    "D2R-Repo": "https://github.com/shallox/d2r-discord-bot"
}


class D2RuneWizardClient():
    @staticmethod
    def terror_zone():
        """
        Returns latest terror zone info.

        :return: string of walk information.
        """
        terror_zone_data = get(
            f'https://d2runewizard.com/api/terror-zone?token={D2RW_TOKEN}',
            headers=headers,
            timeout=10).json()
        terror_info = dict(terror_zone_data)["terrorZone"]
        tz = terror_info["zone"]
        alt_tz = ''
        global last_update
        last_update = datetime.fromtimestamp(terror_info["lastUpdate"]["seconds"])
        for zone in terror_info['reportedZones'].keys():
            if len(terror_info['reportedZones'].keys()) <= 1:
                alt_tz += f'\nNo alternate zones reported.'
            else:
                alt_tz += f'\nReported Zone: {zone}\nPositive reports: {terror_info["reportedZones"]}'
        reply = f':skull_crossbones::skull_crossbones::skull_crossbones::skull_crossbones::skull_crossbones::skull_crossbones::skull_crossbones::skull_crossbones::skull_crossbones::skull_crossbones:\n' \
                f'Current terror zone: {tz}\n' \
                f'Last report @: {last_update}\n' \
                f'Positive reports: {terror_info["highestProbabilityZone"]["amount"]}\n' \
                f'Probability zone is correct: {terror_info["highestProbabilityZone"]["probability"]}\n' \
                f'Disputed terror zone: {alt_tz}\n' \
                f'Data courtesy of d2runewizard.com\n' \
                f':skull_crossbones::skull_crossbones::skull_crossbones::skull_crossbones::skull_crossbones::skull_crossbones::skull_crossbones::skull_crossbones::skull_crossbones::skull_crossbones:'
        print(reply)
        return reply


class DiscordClient(discord.Client):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    """
    Connects to Discord and starts a background task that checks the diablo2.io dclone API every 60 seconds.
    When a progress change occurs that is greater than or equal to DCLONE_THRESHOLD and for more than DCLONE_REPORTS
    consecutive updates, the bot will send a message to the configured DCLONE_DISCORD_CHANNEL_ID.
    """

    async def on_ready(self):
        """
        Runs when the bot is connected to Discord and ready to receive messages. This starts our background task.
        """
        # pylint: disable=no-member
        print(f'Bot logged into Discord as "{self.user}"')
        servers = sorted([g.name for g in self.guilds])
        print(f'Connected to {len(servers)} servers: {", ".join(servers)}')
        # delete
        arr = [client.get_channel(1170022098127822928)]

        for channel in arr:
            print('Clearing messages...')
            await channel.purge(limit=1000)
        else:
            print(channel, 'Keine Eintraege gefunden')

        # channel details
        channel = self.get_channel(CHANEL)
        if not channel:
            print('ERROR: Unable to access channel, please check DCLONE_DISCORD_CHANNEL_ID')
            await self.close()
            return
        print(f'Messages will be sent to #{channel.name} on the {channel.guild.name} server')

        try:
            self.check_tz_status.start()
        except RuntimeError as err:
            print(f'Background Task Error: {err}')

    async def on_message(self, message):
        """
        This is called any time the bot receives a message. It implements the dclone chatop.
        """
        if message.author.bot:
            return

        channel = self.get_channel(message.channel.id)
        if message.content.startswith('!tz'):
            print(f'Providing Terror Zone info to {message.author}')
            await channel.send(D2RuneWizardClient.terror_zone())
            await channel.send(f'{D2RuneWizardClient.terror_zone()}')
        elif message.content.startswith('!help'):
            await channel.send(
                f'Commands are:\n!tz | Displays the latest Terror Zone info.\n!help | ...Provides a clue -.0')

    @tasks.loop(seconds=60)
    async def check_tz_status(self):
        global dt_hour_last
        this_hour = datetime.now()
        if dt_hour_last is None and last_update is None:
            channel = self.get_channel(CHANEL)
            dt_hour_last = datetime.now()
            await channel.send(f'{D2RuneWizardClient.terror_zone()}')
        elif dt_hour_last.hour == this_hour.hour:
            if last_update.hour == this_hour.hour:
                pass
            else:
                channel = self.get_channel(CHANEL)
                dt_hour_last = datetime.hour
                await channel.send(f'{D2RuneWizardClient.terror_zone()}')
        elif dt_hour_last != this_hour:
            msg_data = D2RuneWizardClient.terror_zone()
            if last_update.hour == this_hour.hour:
                channel = self.get_channel(CHANEL)
                dt_hour_last = datetime.now()
                await channel.send(f'{msg_data}')
            else:
                pass


if __name__ == '__main__':
    client = DiscordClient(intents=discord.Intents.default())
    client.run(TOKEN)