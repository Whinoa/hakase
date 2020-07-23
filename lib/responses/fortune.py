import asyncio
import discord
import requests

from lib.client import client

async def fortune(message, params):
  request = requests.get('http://www.yerkee.com/api/fortune')
  if request.status_code != 200: return

  fortune = request.json()['fortune']
  await message.channel.send(fortune)
