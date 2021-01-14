# bot.py
import os
import discord
from dotenv import load_dotenv
import asyncio
import requests
from coinbase.wallet.client import Client
from datetime import date
from datetime import datetime, timedelta



load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

@client.event
async def on_message(message):
    content = message.content.lower().split(' ')
    if content[0] == 'eth' or content[0] == 'btc' and not message.author == client.user:
        crypto = content[0].upper()
        currPair = '%s-EUR'%crypto
        cbClient = Client('0', '0', api_version=str(date.today()))

        response = requests.get("https://api.pro.coinbase.com/products/%s/stats"%currPair)
        data = response.json()
        toSend = """```diff\n%s Stats\n"""%crypto
        toSend += 'Current: €%s \n' % data['last']
        toSend += '24h High: €%s \n' % data['high']
        toSend += '24h Low: €%s \n' % data['low']

        toSend += '\n'

        time1 = str(datetime.now()- timedelta(hours = 1))
        time2 = str(datetime.now())
        response = requests.get("https://api.pro.coinbase.com/products/%s/candles?start=%s&end=%s&granularity=60"%(currPair,time1,time2))
        dataSlice = response.json()
        oneHourPrice = dataSlice[0][3]
        toSend += '1h Ago: €%s\n' % oneHourPrice
        oneHourChange = float(oneHourPrice) - float(data['last'])
        oneHourPercChange = 100.00*(abs(float(oneHourChange))/float(oneHourPrice))
        if oneHourChange < 0:
            toSend += '+ %.3f%% 1h\n' % oneHourPercChange
        else:
            toSend += '- %.3f%% 1h\n' % oneHourPercChange

        time1 = str(datetime.now()- timedelta(hours = 24))
        time2 = str(datetime.now()- timedelta(hours = 23))
        response = requests.get("https://api.pro.coinbase.com/products/%s/candles?start=%s&end=%s&granularity=60"%(currPair,time1,time2))
        dataSlice = response.json()
        oneDayPrice = dataSlice[0][3]
        toSend += '24h Ago: €%s\n' % oneDayPrice
        oneDayChange = float(oneDayPrice) - float(data['last'])
        oneDayPercChange = 100.00*(abs(float(oneDayChange))/float(oneDayPrice))
        if oneDayChange < 0:
            toSend += '+ %.3f%% 24h\n' % oneDayPercChange
        else:
            toSend += '- %.3f%% 24h\n' % oneDayPercChange

        monthHours = 24*31
        #last_month_date_time = datetime.now() - timedelta(hours = monthHours)
        #print(last_month_date_time)
        #oneMonthPrice = cbClient.get_spot_price(currency_pair=currPair,date=last_month_date_time)['amount']
        time1 = str(datetime.now()- timedelta(hours = monthHours))
        time2 = str(datetime.now()- timedelta(hours = monthHours-1))
        response = requests.get("https://api.pro.coinbase.com/products/%s/candles?start=%s&end=%s&granularity=60"%(currPair,time1,time2))
        dataSlice = response.json()
        oneMonthPrice = dataSlice[0][3]
        toSend += 'One Month Ago: €%s\n' % oneMonthPrice
        oneMonthChange = float(oneMonthPrice) - float(data['last'])
        oneMonthPercChange = 100.00*(abs(float(oneMonthChange))/float(oneMonthPrice))
        if oneMonthChange < 0:
            toSend += '+ %.3f%% Month\n' % oneMonthPercChange
        else:
            toSend += '- %.3f%% Month\n' % oneMonthPercChange

        toSend += """```"""
        await message.channel.send(toSend)
client.run(TOKEN)
