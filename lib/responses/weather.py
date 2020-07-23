import asyncio
import discord
import requests

from bs4 import BeautifulSoup

from lib.client import client

async def weather(message, params):
    # %20 = ' ' (a space)
    location = '%20'.join(params)
    headers = {'user-agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
    page = requests.get('http://wttr.in/'+location,headers=headers)
    soup = BeautifulSoup(page.text,'html.parser')
    text = soup.pre.get_text().split('\n')
    #Put in code block
    weather = '```'
    #The first 8 lines (skipping one empty line) of the <pre> element wttr.in returns contain all we need
    for n in range(1,8):
        weather += text[n]+'\n'

    #Finish code block
    weather += '```'

    await message.channel.send(weather)
