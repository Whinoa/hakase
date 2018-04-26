import asyncio
import json
import random
import os
import sys
import datetime
import time
import importlib
from lib import router
from lib.client import client

f = open('config','r')
config = json.load(f)

# def init():


@client.event
async def on_ready():
  print('''Logged in as\n{0}\n{1}\n------
    '''.format(client.user.display_name, client.user.id))

@client.event
async def on_message(message):
  if(message.content== '>reload'):
    importlib.reload(router)
    await client.send_message(message.channel,'Responses reloaded!')
    print(router.response_list)
    await router.list_responses(message,{})
  elif not message.author.bot: 
    await router.respond(message)

client.run(config['client_key'])
