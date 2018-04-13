import asyncio
import discord
import datetime

from lib.client import client
from lib.models import QtAnimeGirl
from hakase import config

# Channels where qtb is in progress


async def get_new_girls(message):
  anime_girl = QtAnimeGirl()
  new_girls = anime_girl.get_new_girls(config['image_directory'])
  await client.send_message(message.channel, "{} new girls added!".format(new_girls))

async def qtb(message, params):
  caller = discord.User()
  girls = [QtAnimeGirl(), QtAnimeGirl()]
  vote = discord.Message(reactions=[])
  votes = [0, 0]
  voters = {}
  is_ongoing = True
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
