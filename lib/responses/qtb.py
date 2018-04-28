import asyncio
import discord
import datetime
import random
import os
import time

from sqlalchemy.orm.exc import NoResultFound
from lib.client import client
from lib.models import QtAnimeGirl, Tag, session
from hakase import config

# Channels where qtb is in progress
ongoing_qtb = []

async def get_new_girls(message, params):
  anime_girl = QtAnimeGirl()
  new_girls = anime_girl.get_new_girls(config['image_directory'])
  await client.send_message(message.channel, "{} new girls added!".format(new_girls))

async def qtb(message, params):
  if message.channel in ongoing_qtb:
    warning = await client.send_message(message.channel, 'One QTB per channel at a time please.')

    await asyncio.sleep(10)
    client.delete_message(warning)

    return

  ongoing_qtb.append(message.channel)

  caller= message.author
  girls= [QtAnimeGirl(), QtAnimeGirl()]
  vote= discord.Message(reactions=[])
  votes= [0, 0]
  voters= {}
  is_ongoing= True

  all_girls= []

  if not params:
    all_girls= session.query(QtAnimeGirl).all()
  else:
    for param in params:
      try:
        tag= session.query(Tag).filter(Tag.tag == param).one()
        girls_with_tag= tag.qtanimegirls
        for girl in girls_with_tag:
          if girl not in all_girls:
            all_girls.append(girl)
      except NoResultFound:
        pass
  
    if len(all_girls < 2):
      tmp= await client.send_message(message.channel,
        "Couldn't find enough girls with provided tags, using random girls")
      all_girls= session.query(QtAnimeGirl).all()
      
  girls = random.sample(list(all_girls), 2)

  for girl in girls:
    await client.send_typing(message.channel)
    await client.send_file(message.channel,
      open(os.path.join(config['image_directory'], girl.image), 'rb'),
      filename= girl.image,
      content= '{0} with a {1} ranking'.format(girl, girl.elo)
    )
  
  try:
    await client.delete_message(tmp)
  except:
    pass
  
  vote = await client.send_message(message.channel,
    '{0} vs {1} - 0 - 0'.format(girls[0], girls[1])
  )

  # timeout = time.time() + 60 * 5 # 5 minutes from now
  timeout = time.time() + 10

  while is_ongoing:
    # Check if timed out
    if timeout < time.time():
      break
    action = await client.wait_for_message(
      channel= message.channel,
      check= lambda msg:
        msg.content.startswith('>vote') or (msg.content.startswith('>end') and msg.author.id == caller.id),
      timeout=5
    )

    if not action:
      continue

    if action.content.startswith('>end'):
      break

    # Gets first digit
    # See: https://stackoverflow.com/a/20008559
    try:
      action_vote = int(action.content[[char.isdigit() for char in action.content].index(True)])
    except ValueError:
      continue
    
    if action_vote in [1,2]:
      if action.author.id not in voters or action_vote != voters[action.author.id]:
        if action.author.id in voters:
          votes[voters[action.author.id] - 1] -= 1
        voters[action.author.id] = action_vote
        votes[action_vote - 1] += 1
    await client.edit_message(vote, new_content='{0} vs {1} - {2} - {3}'.format(girls[0],girls[1],votes[0],votes[1]))
  

  draw = votes[0] == votes[1]

  if not draw:
    winner = 1 if max(votes[0], votes[1]) == votes[0] else 2
    loser = 3 - winner
    winner = girls[winner - 1]
    loser = girls[loser - 1]

    # Update ELO ratings
    oldElo = winner.elo
    winner.updateELO(loser.elo, 1)
    loser.updateELO(winner.elo, 0)

    # Print results
    await client.send_message(message.channel, '{0} wins! Her rating is now {1}(+{2})'.format(
      winner,winner.elo, winner.elo - oldElo
    ))

  else:
    oldElo1 = girls[0].elo
    oldElo2 = girls[1].elo

    girls[0].updateELO(girls[1].elo, 0.5)
    girls[1].updateELO(girls[0].elo, 0.5)


    await client.send_message(message.channel, 'It\'s a tie! QTR change: {0} ({1}) {2} ({3})'.format(
      girls[0], girls[0].elo - oldElo1, girls[1], girls[1].elo - oldElo2
    ))
    
  ongoing_qtb.remove(message.channel)
