import asyncio
import discord
import datetime
import random
import os

from sqlalchemy.orm.exc import NoResultFound
from lib.client import client
from lib.models import QtAnimeGirl, Tag, session
from hakase import config

# Channels where qtb is in progress
ongoing_qtb = []

async def get_new_girls(message):
  anime_girl = QtAnimeGirl()
  new_girls = anime_girl.get_new_girls(config['image_directory'])
  await client.send_message(message.channel, "{} new girls added!".format(new_girls))

async def qtb(message, params):
  if message.channel in ongoing_qtb:
    return
  ongoing_qtb.append(message.channel)

  caller= discord.User()
  girls= [QtAnimeGirl(), QtAnimeGirl()]
  vote= discord.Message(reactions=[])
  votes= [0, 0]
  voters= {}
  is_ongoing= True
  time_start= datetime.datetime.now()

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
      filename= girls.image,
      content= '{0} with a {1} ranking'.format(girl, girl.elo)
    )
  
  try:
    await client.delete_message(tmp)
  except:
    pass
  
  vote = await client.send_message(message.channel,
    '{0} vs {1} - 0 - 0'.format(girls[0], girls[1])
  )
  time_start = datetime.datetime.now()

  


# QTB
# 1. Send start message
# 2. Get 2 random qts or get them from tags
# 3. Send qts
# 4. Start voting
# 5. Collect votes
# 6. End battle
# 7. Update girl scores
# 8. Present results 
