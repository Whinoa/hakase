import asyncio
import discord
import datetime
import random
import os
import time

from sqlalchemy.orm.exc import NoResultFound
from lib.utils.str_get_first_number import str_get_first_number
from lib.client import client
from lib.models import QtAnimeGirl, Tag, session

from hakase import config

# Channels where qtb is in progress
ongoing_qtb = []

async def get_new_girls(message, params):
  anime_girl = QtAnimeGirl()
  new_girls = anime_girl.get_new_girls(config['image_directory'])
  await client.send_message(message.channel, "{} new girls added!".format(new_girls))

def _check_for_qtb_command(message):
  command = message.content[:2].lower()

  # Only check first 2 characters here
  if command in ['>v', '>e', '>n', '>t', '>t']:
    return True
  else:
    return False

async def _name_girl(message, girls):
  index = str_get_first_number(message.content) - 1
  girl = girls[index]

  name = message.content[5:]

  girl.name = name
  session.commit()

  await client.send_message(message.channel, 'Girl {0} now known as {1}!'.format(girl.id, girl.name))

async def _get_tags(message, girls):
  tags = []
  index = str_get_first_number(message.content) - 1
  girl = girls[index]

  for tag in girl.tags:
    tags.append(tag.tag)

  await client.send_message(message.channel, '{0}\'s tags: {1}'.format(girl, ', '.join(tags)))

async def _set_tags(message, girls):
  index = str_get_first_number(message.content) - 1
  girl = girls[index]

  split_content = message.content.split(' ')
  tags = split_content[2].split(',')

  for tag in tags:
    girl.addTag(tag)

  await client.send_message(message.channel, 'Tags {0} added to {1}'.format(', '.join(tags), girl))


async def _get_girls(message, params= None):
  all_girls= []

  if params:
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
      await client.send_message(message.channel,
        "Couldn't find enough girls with provided tags, using random girls")
      all_girls= session.query(QtAnimeGirl).all()
  else:
    all_girls= session.query(QtAnimeGirl).all()

  return random.sample(list(all_girls), 2)

async def _parse_vote(message, voters, votes):
    try:
      vote = str_get_first_number(message.content)
    except ValueError:
      return None

    if vote in [1,2]:
      if message.author.id not in voters or vote != voters[message.author.id]:
        if message.author.id in voters:
          votes[voters[message.author.id] - 1] -= 1
        voters[message.author.id] = vote
        votes[vote - 1] += 1

    return {'votes': votes, 'voters': voters}

async def _resolve_battle(message, votes, girls):
  draw = votes[0] == votes[1]

  if not draw:
    # Winners index
    winner = 0 if max(votes[0], votes[1]) == votes[0] else 1
    # Losers index
    loser = 1 - winner
    winner = girls[winner]
    loser = girls[loser]

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



async def qtb(message, params):
  if message.channel in ongoing_qtb:
    warning = await client.send_message(message.channel, 'One QTB per channel at a time please.')

    await asyncio.sleep(10)
    client.delete_message(warning)

    return

  ongoing_qtb.append(message.channel)

  caller= message.author
  girls= [QtAnimeGirl(), QtAnimeGirl()]
  votes= [0, 0]
  voters= {}
  is_ongoing= True

  girls = await _get_girls(message, params)

  for girl in girls:
    await client.send_typing(message.channel)
    await client.send_file(message.channel,
      open(os.path.join(config['image_directory'], girl.image), 'rb'),
      filename= girl.image,
      content= '{0} with a {1} ranking'.format(girl, girl.elo)
    )

  tally = await client.send_message(message.channel,
    '{0} vs {1} - 0 - 0'.format(girls[0], girls[1])
  )

  timeout = time.time() + 60 * 5 # 5 minutes from now

  while is_ongoing:
    # Check if timed out
    if timeout < time.time() and len(voters) > 1:
      break
    action = await client.wait_for_message(
      channel= message.channel,
      check= _check_for_qtb_command,
      timeout=5
    )

    if not action:
      continue

    if action.content.startswith('>name'):
      await _name_girl(action, girls)
      continue

    if action.content.startswith('>tag '):
      await _set_tags(action, girls)
      continue

    if action.content.startswith('>tags'):
      await _get_tags(action, girls)
      continue

    if action.content.startswith('>end') and action.author.id == caller.id:
      break

    result = await _parse_vote(action, voters, votes)

    if result:
      voters = result['voters']
      votes  = result['votes']

      await client.edit_message(tally, new_content='{0} vs {1} - {2} - {3}'.format(girls[0],girls[1],votes[0],votes[1]))

  await _resolve_battle(message, votes, girls)
  ongoing_qtb.remove(message.channel)
