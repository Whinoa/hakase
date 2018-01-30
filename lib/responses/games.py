import asyncio
import random
import discord
import requests

from lib.client import client

# Utility functions
# For Jeopardy

def __map_to_mentions(array):
  def to_mention(user):
    return user.mention

  return ", ".join(map(to_mention,array))

def __get_clues():
  # Get categories
  def get_random_category():
    seed_clue = requests.get('http://jservice.io/api/random').json()[0]
    cat_id = seed_clue['category']['id']
    category = requests.get('http://jservice.io/api/category?id={}'.format(cat_id)).json()
    return category

  categories = []
  for i in range(6):
    categories.append(get_random_category())

  # Filter clues
  def get_one_by_value(clues, value):
    def compare(a):
      print(a,value)
      return a['value'] == value
    clues = list(filter(compare, clues))
    # if len(clues) > 1:
      # clue = random.sample(clues, 1)[0]
    if len(clues) >= 1:
      clue = clues[0]
    else:
      return False
    
    return clue
  
  def get_one_of_each_value(clues):
    hundred = get_one_by_value(clues, 100)
    two_hundred = get_one_by_value(clues, 200)
    three_hundred = get_one_by_value(clues, 300)
    four_hundred = get_one_by_value(clues, 400)
    five_hundred = get_one_by_value(clues, 500)
    if hundred and two_hundred and three_hundred and four_hundred and five_hundred:
      array = [hundred,two_hundred,three_hundred,four_hundred,five_hundred]
      return [hundred,two_hundred,three_hundred,four_hundred,five_hundred]
    else: 
      return False

  for category in categories:
    clues = category['clues']
    clues = get_one_of_each_value(clues)
    if clues:
      category['clues'] = clues
    # Category was incomplete, try to find a complete one
    else:
      while not clues or len(clues) != 5:
        category = get_random_category()
        clues = get_one_of_each_value(category['clues'])
        if clues:
          category['clues'] = clues
  
  return categories

def __make_board(categories):
  embed=discord.Embed(color=0x2a25ff)
  def list_unsolved(clues):
    unsolved = filter(lambda x: not 'solved' in x, clues)
    return ', '.join(map(lambda x: str(x['value']), unsolved))

  for index, category in enumerate(categories):
    embed.add_field(name='({}) {}'.format(index + 1,category['title'].title()), value= list_unsolved(category['clues']))

  return embed

async def jeopardy(message,params):
  print('Starting Jeopardy')
  players = [message.author]
  categories = __get_clues()
  # await client.send_typing(message.channel)
  # await client.send_message(message.channel, 'This is Jeopardy!')
  # await client.send_message(message.channel, 'With your host: Hakase!')
  # # Get categories
  # await client.send_message(message.channel, 'Join the game with >join. You need 3 players to start.')
  # participant_message = await client.send_message(message.channel, 'Playing: {}'.format(__map_to_mentions(players)))
  # for i in range(1):
  #   join_message = await client.wait_for_message(channel=message.channel, content=">join")
  #   if join_message.author not in players:
  #     players.append(join_message.author)
  #     await client.send_message(message.channel, '{} has joined the game'.format(join_message.author.mention))
  #     await client.edit_message(participant_message, 'Playing: {}'.format(__map_to_mentions(players)))
  #   await client.delete_message(join_message)
  # await client.send_message(message.channel, 'Starting game!')
  await client.send_message(message.channel, embed=__make_board(categories))
  
  # def game_loop():

  

#TODO: 
# 0: GREET AUDIENCE
# 1: GET CATEGORIES
# 1.5: GET CONTESTANTS
# 2: CLUES FROM CATEGORIES
# 3: SORT AND FILTER CLUES
# 4: PRESENT CLUES
# 5: ASK FOR SELECTION OF CATEGORY
# 6: GET THE REPLY
# 7: PRESENT CLUE
# 8: GET BEEPS
# 8.1 COUNTDOWN FOR ANSWER
# 8.2 GET ANSWER
# 9: CHECK FOR CORRECT
# 10: ADD OR REDUCE MONEY
# 11: IF INCORRECT WAIT FOR OTHERS TO ANSWER AND REPEAT FROM #7 UNTILL SOMOEONE ANSWERS OR TIME OUT
# 12: REPEAT FROM #5 UNTILL BOARD CLEAR
# 13: Congraluate winnner, mock losers
# 14: LOG USER TOTALS for leaderboards

