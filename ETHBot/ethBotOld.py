# bot.py
import os
import discord
from dotenv import load_dotenv
import asyncio
import requests
import coinbase

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

@client.event
async def on_message(message):
    content = message.content.lower().split(' ')
    if content[0] == 'eth' and not message.author == client.user:
        response = requests.get("https://api.pro.coinbase.com/products/ETH-EUR/stats")
        data = response.json()
        toSend = '\n ETH Stats:\n'
        toSend += 'Current: €%s \n' % data["last"]
        toSend += '24h High: €%s \n' % data["high"]
        toSend += '24h Low: €%s \n' % data["low"]
        await message.channel.send(toSend)

client.run(TOKEN)
