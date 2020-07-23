import asyncio
import random

from lib.client import client

async def rand(message, params):
    max = int(params[0])
    mention = message.author.mention
    result = random.randint(0, max)
    response = '{} rolled **{}**'.format(mention, result)
    await message.channel.send(response)

    return response

async def ayy(message, params):
    response = 'lmao' + message.content[3:]

    await message.channel.send(response)

async def avatar(message, params):
    for user in message.mentions:
        await message.channel.send(user.avatar_url)

async def choose(message, params):
    options = message.content[7:].split(';')
    await message.channel.send("I chose `"+ random.choice(options) +"`")

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

    await message.channel.send(reply)

async def turtle(message, params):
    await message.channel.send('''```
  _
 (*\.-.
  \/___\_
   U   U
        ```''')
