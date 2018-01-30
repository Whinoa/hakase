import asyncio
import random

from lib.client import client

async def rand(message,params):
  max = int(params[0])
  mention = message.author.mention
  result = random.randint(0, max)
  response = '{} rolled **{}**'.format(mention, result)
  await client.send_message(message.channel, response)

  return response

async def ayy(message,params):
  response = 'lmao' + message.content[3:]

  await client.send_message(message.channel, response)