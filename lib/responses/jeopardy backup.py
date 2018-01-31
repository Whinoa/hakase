import asyncio
import random
import discord
import json
import re

from lib.client import client

def __validate_category(category):
  clues = category['clues']
  if len(clues) != 5:
    return False
  for n in range(0,5):
    if clues[n]['value'] != (n + 1) * 2 * 100:
      return False
  return True

def __get_clues():
  # Retrieves 6 categories with 5 clues each
  clue_file = open('lib/responses/questions.json')
  store = json.loads(clue_file.read())
  # Holds final categories in a pre-parsed state, used for duplicate checking
  selected_categories = []
  # The return value
  final_categories = []
  while len(final_categories) != 6:
    # Candidate category
    candidate = random.choice(store)
    while candidate in selected_categories:
      candidate = random.choice(store)
    clues = candidate["clues"]
    # Filter out final jeopardy clues
    clues = list(filter(lambda x: x['value'] != None, clues))
    if len(clues) < 1:
      continue
    lowest_clue_value = min(clues, key=(lambda x: x['value']))['value']
    # Discard category if it's from double jeopardy
    # TODO: Implement double jeopardy
    if lowest_clue_value >= 400:
      continue
    
    #Get 5 clues with values 100,200,300,400 and 500
    selected_clues = []
    for i in range(0,5):
      potential_clues = list(filter(lambda x: x['value'] == (i + 1) * 2 * 100, clues))
      try: 
        selected_clues.append(random.choice(potential_clues))
      except IndexError:
        continue

    candidate['clues'] = selected_clues
    if __validate_category(candidate):
      final_categories.append(candidate)
    else:
      print('Not valid')

  return final_categories



def messageToClue(msg, categories):
	cat_params = msg.content.split(' ')
	question_category = categories[int(cat_params[0]) - 1]
	return {
    'clue': question_category['clues'][round(int(cat_params[2]) / 200 - 1)],
    'category': question_category
  }


def __make_board(categories):
  embed=discord.Embed(color=0x2a25ff)
  def list_unsolved(clues):
    unsolved = filter(lambda x: not 'solved' in x, clues)
    return ', '.join(map(lambda x: str(x['value']), unsolved))

  for index, category in enumerate(categories):
    for remaining in list_unsolved(category['clues']).split("\n"):
      if remaining != '':
        embed.add_field(name='({}) {}'.format(index + 1,category['title'].title()), value = list_unsolved(category['clues']))
      else:
        embed.add_field(name='({}) {}'.format(index + 1,category['title'].title()), value = 'No more clues in this category!')
  return embed
    
def __map_to_mentions(dict):
  def to_mention(user):
    return user[1]['user'].mention

  return ", ".join(map(to_mention,dict.items()))

async def jeopardy(message,params):
  # STATE
  players = {
    message.author.id: {
      'user': message.author,
      'points': 0
    }
    
  }
  selection_priority = message.author
    
  categories = __get_clues()
  finished = False
  await client.send_typing(message.channel)
  await client.send_message(message.channel, 'This is Jeopardy!')
  await client.send_message(message.channel, 'With your host: Hakase!')
  await client.send_message(message.channel, 'Join the game with >join. You need 3 players to start.')
  participant_message = await client.send_message(message.channel, 'Playing: {}'.format(__map_to_mentions(players)))
  for i in range(2):
    join_message = await client.wait_for_message(channel=message.channel, content=">join")
    if join_message.author not in players:
      players[join_message.author.id] = {
        'user':join_message.author,
        'points': 0
      }
      await client.send_message(message.channel, '{} has joined the game'.format(join_message.author.mention))
      await client.edit_message(participant_message, 'Playing: {}'.format(__map_to_mentions(players)))
    await client.delete_message(join_message)
  await client.send_message(message.channel, 'Starting game!')
  def get_selection(msg):
    regex = r"\d\s(for)\s(200|400|600|800|1000)"
    match = re.match(regex,msg.content)
    if match and msg.author == selection_priority:
      return True
    else:
      return False
   
  while not finished:
    await client.send_message(message.channel, embed=__make_board(categories))
    await client.send_message(message.channel, '{} has the board.'.format(selection_priority.mention))
    await client.send_message(message.channel, 'Please select a category with "x for y"')
    category_selection = await client.wait_for_message(channel=message.channel, check=lambda x: get_selection(x) == True)
    choice = messageToClue(category_selection, categories)
    question = discord.Embed(color=0x2a25ff)
    if 'solved' in choice['clue']:
      await client.send_message(message.channel, 'We already did that one, baka')
      continue
    choice['clue']['solved'] = 'solved'
    question.add_field(name=choice['category']['title'].title(), value=choice['clue']['question'])
    await client.send_message(message.channel, embed=question)
    await client.send_message(message.channel, 'Buzz in with >beep')
    guesser = await client.wait_for_message(
      channel=message.channel,
      check=lambda x: x.author.id in players and '>b' in x.content  
    )
    await client.send_message(message.channel, 'You have 20 seconds!')
    guess = await client.wait_for_message(timeout = 20, author = guesser.author, channel = message.channel)
    if not guess:
      continue
    else:
      if guess.content.lower() in choice['clue']['answer'].lower():
        await client.send_message(message.channel, 'CORRECT! You get {} points'.format(choice['clue']['value']))
        await client.send_message(message.channel, 'You now have {} points!'.format(players[guess.author.id]['points'] + choice['clue']['value']))
        players[guess.author.id]['points'] += choice['clue']['value']
        selection_priority = guess.author
      else:
        await client.send_message(message.channel, 'Wrong! You lose {} points'.format(choice['clue']['value']))
        players[guess.author.id]['points'] -= choice['clue']['value']
        await client.send_message(message.channel, 'You now have {} points!'.format(players[guess.author.id]['points']))
        await client.send_message(message.channel, 'The answer was: {}'.format(choice['clue']['answer']))


