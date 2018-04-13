
import asyncio
import random
import discord
import random
import time

from lib.client import client


racers = "🐶 🐱 🐭 🐹 🐰 🦊 🐻 🐼 🐨 🐯 🦁 🐮 🐷 🐽 🐸 🐧 🐦 🦅 🦉 🦇 🦋 🐌 🦀 🦑 🐢 🐍".split(" ")
racing = []

def get_racer():  
  racer = racers[round(random.random()*len(racers) - 1)]
  if racer not in racing:
    return racer
  else:
    return get_racer()
    
def __map_to_mentions(dict):
  def to_mention(user):
    return user[1]['user'].mention

  return ", ".join(map(to_mention,dict.items()))
    
def check_nickname(sender):
  if sender.nick == None:
    return sender.name
  else:
    return sender.nick


async def race(message,params):
  # STAT
  players = {
    message.author.id: {
      'user': message.author,
      'racer': get_racer(),
      'name': check_nickname(message.author)
    }
  }
  racing.append(players[message.author.id]['racer'])
  
  await client.send_message(message.channel, 'Welcome to the race! 🏁\nJoin the race with >join.\nContestants have 30 seconds to join!')
  endtime = time.time() + 30
  await client.send_message(message.channel, '{} has joined the race! Your racer is {}!'.format(players[message.author.id]['name'], players[message.author.id]['racer']))
  participant_message = await client.send_message(message.channel, 'Playing: {}'.format(__map_to_mentions(players)))
  while True:
    join_message = await client.wait_for_message(timeout = endtime - time.time(), channel=message.channel, content=">join")
    if not join_message:
      break
    if join_message.author.id not in players:
      players[join_message.author.id] = {
        'user':join_message.author,
        'racer': get_racer(),
        'name': check_nickname(join_message.author)
      }
      await client.send_message(message.channel, '{} has joined the race! Your racer is {}!'.format(join_message.author.mention, players[join_message.author.id]['racer']))
      await client.edit_message(participant_message, 'Playing: {}'.format(__map_to_mentions(players)))
    await client.delete_message(join_message)
  await client.send_message(message.channel, 'The race begins! 🏁')