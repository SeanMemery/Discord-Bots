# bot.py
import os
import discord
from dotenv import load_dotenv
import requests
from datetime import date
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np



load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

currencies = ['EUR','USD','GBP']
currencySign = ['€','$','£']
currency = 0

def getPastPrice(hours, currPair, timeString, data):
    time1 = str(datetime.now()- timedelta(hours = hours))
    time2 = str(datetime.now()- timedelta(hours = hours-1))
    response = requests.get("https://api.pro.coinbase.com/products/%s/candles?start=%s&end=%s&granularity=60"%(currPair,time1,time2))
    dataSlice = response.json()
    pastPrice = dataSlice[0][3]
    toSend = '%s Ago: %s%s\n' % (timeString,currencySign[currency],pastPrice)
    change = float(pastPrice) - float(data['last'])
    percChange = 100.00*(abs(float(change))/float(pastPrice))
    if change < 0:
        toSend += '+ %.3f%% %s\n' % (percChange,timeString)
    else:
        toSend += '- %.3f%% %s\n' % (percChange,timeString)
    return toSend


@client.event
async def on_message(message):
    content = message.content.lower()
    input = message.content.split()
    if not message.author == client.user and len(content)>0 and content[0] == '!':
        crypto = input[0][1:].upper()
        if (len(input)>1) and input[1].upper() in currencies:
            currency = currencies.index(input[1].upper())
        else:
            currency = 0
        currPair = '%s-%s'%(crypto,currencies[currency])
        print(message.author, crypto, datetime.now())

        print(currPair)

        response = requests.get("https://api.pro.coinbase.com/products/%s/stats"%currPair)
        data = response.json()
        toSend = """```diff\n%s Stats\n"""%crypto
        toSend += 'Current: %s%s \n' % (currencySign[currency],data['last'])
        toSend += '24h High: %s%s \n' % (currencySign[currency],data['high'])
        toSend += '24h Low: %s%s \n' % (currencySign[currency],data['low'])

        toSend += '\n'

        toSend += getPastPrice(1,currPair,'1h',data)
        toSend += getPastPrice(24,currPair,'24h',data)
        toSend += getPastPrice(24*31,currPair,'1 Month',data)

        toSend += """```"""
        await message.channel.send(toSend)


        ### SENDING GRAPH
        if 'graph' in input:
                print('Making Graph')
                timeIntervals = 3600
                response = requests.get("https://api.pro.coinbase.com/products/%s/candles?granularity=%d"%(currPair,timeIntervals))
                dataSlice = response.json()
                pastPrices_y = []
                for i in dataSlice:
                    pastPrices_y.append(i[3])
                numDays = int(len(pastPrices_y)/24)
                x = list(range(0,len(pastPrices_y)))
                x.reverse()
                pastPrices_y.reverse()
                fig, ax = plt.subplots()

                ax.plot(x, pastPrices_y)
                ax.set_xlim(len(x), 0)  # decreasing time
                ax.yaxis.tick_right()
                ax.set_title('%s Graph'%currPair)
                ax.set_xlabel('Days')
                ax.set_ylabel(currPair)
                ###
                ticks = np.arange(0, x[0], step=24)
                ###
                plt.xticks(ticks,list(range(0,numDays+1)))
                fig.savefig(fname='plot')
                await message.channel.send(file=discord.File('plot.png'))
                os.remove('plot.png')






client.run(TOKEN)
