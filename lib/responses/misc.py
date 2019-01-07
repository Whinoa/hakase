import asyncio
import random

from lib.client import client

async def rand(message, params):
    max = int(params[0])
    mention = message.author.mention
    result = random.randint(0, max)
    response = '{} rolled **{}**'.format(mention, result)
    await client.send_message(message.channel, response)

    return response

async def ayy(message, params):
    response = 'lmao' + message.content[3:]

    await client.send_message(message.channel, response)

async def avatar(message, params):
    for user in message.mentions:
        await client.send_message(message.channel,user.avatar_url)

async def choose(message, params):
    options = message.content[7:].split(';')
    await client.send_message(message.channel,"I chose `"+ random.choice(options) +"`")

async def e(message, params):
    arguments = message.content.split(' ')
    if len(arguments) > 1 and random.random() > 0.1 :
        reply = message.content[1:] + ' did it :unamused: :gun:'
    elif len(arguments) > 1 :
        reply = client.user.mention + ' did it :unamused: :gun:'
    elif len(arguments) == 1 :
        if random.random() > 0.3 :
            reply = message.author.mention + ' did it :unamused: :gun:'
        else:
            reply = client.user.mention + ' did it :unamused: :gun:'
            
    await client.send_message(message.channel, reply)

async def turtle(message, params):
    await client.send_message(message.channel, '''```
  _
 (*\.-.
  \/___\_
   U   U
        ```''')
