# -*- coding: iso-8859-1 -*-
import asyncio

import discord
client = discord.Client(intents=discord.Intents.default())
TOKEN = ('')
def main():
    @client.event
    async def on_ready():
        amount = 100
        # delete
        arr = [client.get_channel()]

        for channel in arr:
            print('Clearing messages...')
            await channel.purge(limit=amount)
            await asyncio.sleep(6)
        else:
            print(channel, 'Keine Eintraege gefunden')



if __name__ == '__main__':
    main()
    client.run(TOKEN)