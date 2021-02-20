import json
### 0: Success
### -1: Invalid amount to give
### -2: Unknown username
### -3: Unknown key
### -4: Not enough coins to give


class WalletsManager:
    def __init__(self):
        self.usernamesDict = {}
        self.walletsDict = {}
        try:
            with open('walletsDict.json', 'r') as fp:
                self.walletsDict = json.load(fp)
        except FileNotFoundError as e:
            print('invalid json: %s' % e)
        try:
            with open('usernamesDict.json', 'r') as fp:
                self.usernamesDict = json.load(fp)
        except FileNotFoundError as e:
            print('invalid json: %s' % e)

    def SaveDicts(self):
        with open('walletsDict.json', 'w') as fp:
            json.dump(self.walletsDict, fp)
        with open('usernamesDict.json', 'w') as fp:
            json.dump(self.usernamesDict, fp)

    def GetBalance(self, key):
        try:
            balance = self.walletsDict[key]
        except KeyError as e:
            print('Cant find key: %s' % e)
            return -3
        return balance

    def GiveFromBot(self, username1, amount):
        try:
            amount = float(amount)
        except ValueError as e:
            print('Invalid amount: %s' % e)
            return -1
        try:
            key1 = self.usernamesDict[username1]
        except KeyError as e:
            print('Cant find username: %s' % e)
            return -2
        try:
            balance1 = self.walletsDict[key1]
        except KeyError as e:
            print('Cant find key: %s' % e)
            return -3
        if balance1 >= amount:
            self.walletsDict[key1] = balance1+amount
            return 0
        else:
            return -4

    def Give(self, username1, username2, amount):
        if username1==username2:
            print('Same usernames')
            return -5
        try:
            amount = float(amount)
        except ValueError as e:
            print('Invalid amount: %s' % e)
            return -1
        try:
            key1 = self.usernamesDict[username1]
            key2 = self.usernamesDict[username2]
        except KeyError as e:
            print('Cant find username: %s' % e)
            return -2
        try:
            balance1 = self.walletsDict[key1]
            balance2 = self.walletsDict[key2]
        except KeyError as e:
            print('Cant find key: %s' % e)
            return -3
        if balance1 >= amount:
            self.walletsDict[key1] = balance1-amount
            self.walletsDict[key2] = balance2+amount
            return 0
        else:
            return -4

    def AddWallet(self, username, key, defaultAmount = 10):
        try:
            balance = self.walletsDict[key]
        except KeyError as e:
            print('New wallet: %s' % e)
            self.walletsDict[key] = defaultAmount
            self.usernamesDict[username] = key
            return True
        ### Need to check if username was changed, then uodate username dictionary to correct key
        try:
            key1 = self.usernamesDict[username] ## if gets to here and fails then username was changed
        except KeyError as e:
            print('Username changed: %s' % e)
            for u, k in self.usernamesDict.items():
                if k==key:
                    self.usernamesDict[username]=k
                    del self.usernamesDict[u]
                    break
        return False

import discord
from dotenv import load_dotenv
import os
import asyncio
from discord.ext import commands
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents().all()
client = discord.Client(intents=intents)
wManager = WalletsManager()


@client.event
async def on_member_join(member):
    tag = str(message.author).split('#')
    username = tag[0]
    usernameLow = tag[0].lower()
    discriminator = tag[1]
    if AddWallet(usernameLow, discriminator):
        await member.channel.send('New wallet made for '+username+' with 10 fcoins, enjoy.')
        wManager.SaveDicts()

@client.event
async def on_message(message):

    if message.author == client.user:
        return

    tag = str(message.author).split('#')
    username = tag[0]
    usernameLow = tag[0].lower()
    discriminator = tag[1]

    if wManager.AddWallet(usernameLow,discriminator):
        await message.channel.send('New wallet made for '+username+' with 10 fcoins, enjoy.')
        wManager.SaveDicts()

    content = message.content.split(' ')

    if message.content[0]=='!' and content[0][1:].lower() == 'give':
        username1 = usernameLow
        username2 = content[1].lower()
        result = wManager.Give(username1, username2, content[2])
        if result == 0:
            await message.channel.send('Coins given!')
        elif result == -1:
            await message.channel.send('Invalid amount, no coins given!')
        elif result == -2:
            await message.channel.send('Unkown username, no coins given!')
        elif result == -3:
            await message.channel.send('Username unknown to bot, no coins given!')
        elif result == -4:
            await message.channel.send('You dont have enough fcoins!')
        elif result == -5:
            await message.channel.send('You cant give fcoins to yourself!')
        wManager.SaveDicts()

    if message.content[0]=='!' and content[0][1:].lower() == 'fcoins':
        result = wManager.GetBalance(discriminator)
        if result >= 0:
            await message.channel.send('%s has %.2f coins' %(username, result))
        elif result == -2:
            await message.channel.send('Unkown username, cant find balance!')
        elif result == -3:
            await message.channel.send('Username unknown to bot, cant find balance!')
        wManager.SaveDicts()

@client.event
async def on_ready():
    client.loop.create_task(GiveLoop(wManager,client,getVChannel(),getTChannel()))

def getVChannel():
    return client.get_channel(351430073263456256)
def getTChannel():
    return client.get_channel(185774053221466119)

async def GiveLoop(wManager,client,vchannel,tchannel):
    microAmount = 0.01
    while True:
        for member in vchannel.members:
            username = str(member).split('#')[0].lower()
            wManager.GiveFromBot(username,microAmount)
        await asyncio.sleep(60)

client.run(TOKEN)
