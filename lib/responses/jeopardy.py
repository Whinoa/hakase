import asyncio
import random
import discord
import json
import re

from fuzzywuzzy import fuzz
from fuzzywuzzy import process
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
    'category': question_category,
    'question': discord.Embed(color=0x2a25ff)
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

async def getBoard(cats, prio, channel):
    await client.send_message(channel, embed=__make_board(cats))
    await client.send_message(channel, '{} has the board.'.format(prio.mention))
    await client.send_message(channel, 'Please select a category with "x for y"')

async def checkGuess(players, guess, clue, channel, priority):
  if fuzz.ratio(guess.content.lower(), clue['answer'].lower()) > 80:
    await client.send_message(channel, 'CORRECT! You get {} points!'.format(clue['value']))
    players[guess.author.id]['points'] += 200
    return {
      'answer': "correct",
      'prio': players[guess.author.id]
    }
  else:
    await client.send_message(channel, 'Wrong! You lose {} points!'.format(clue['value']))	
    players[guess.author.id]['points'] -= clue['value']
    await client.send_message(channel, "The answer was: '{}'".format(clue['answer']))
    return {
      'answer': "incorrect"
    }

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
  await client.send_message(message.channel, 'This is Jeopardy!\nWith your host: Hakase!\nJoin the game with >join. You need 3 players to start.')
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
    await getBoard(categories, selection_priority, message.channel)
    category_selection = await client.wait_for_message(channel=message.channel, check=lambda x: get_selection(x) == True)
    choice = messageToClue(category_selection, categories)

    if 'solved' in choice['clue']:
      await client.send_message(message.channel, 'We already did that one, baka')
      continue

    choice['clue']['solved'] = 'solved'
    choice['question'].add_field(name=choice['category']['title'].title(), value=choice['clue']['question'])
    await client.send_message(message.channel, embed=choice['question'])
    await client.send_message(message.channel, 'Buzz in with >beep, you have 10 seconds to buzz in!')
    
    guesser = await client.wait_for_message(
      timeout = 10,
      channel=message.channel,
      check=lambda x: x.author.id in players and '>b' in x.content  
      )

    if not guesser:
      await client.send_message(message.channel, "Time's up! The correct answer was: '{}'!".format(choice['clue']['answer']))
      continue

    await client.send_message(message.channel, 'You have 20 seconds!')
    
    guess = await client.wait_for_message(
      timeout = 20,
      author = guesser.author,
      channel = message.channel
      )
   
    if not guess:
      #if current contestant doesn't answer, ask others
      await client.send_message(message.channel, "Time's up! You lose {} points".format(choice['clue']['value']))
      players[guesser.author.id]['points'] -= choice['clue']['value']
      await client.send_message(message.channel, 'You now have {} points!'.format(players[guesser.author.id]['points']))
      #TODO turn the whole asking again bit into a function so it can be reused to not only work after no guess but also after an incorrect guess
      await client.send_message(message.channel, 'Would anyone else try their luck? You have 10 seconds to buzz in!')
      
      guesser = await client.wait_for_message(
        timeout = 10,
        channel=message.channel,
        check=lambda x: x.author.id in players and '>b' in x.content  
        )

      if not guesser:
        await client.send_message(message.channel, "Time's up! The correct answer was: '{}'!".format(choice['clue']['answer']))
        continue

      await client.send_message(message.channel, 'You have 20 seconds!')
    
      guess = await client.wait_for_message(
        timeout = 20,
        author = guesser.author,
        channel = message.channel
        )
      
      await checkGuess(players, guess, choice['clue'], message.channel, selection_priority)

      continue
    
    
    result = await checkGuess(players, guess, choice['clue'], message.channel, selection_priority)
    if result['answer'] == "correct":
      selection_priority = result['prio']
      continue
    if result['answer'] == "incorrect":
      await client.send_message(message.channel, "ayy lmao")
      #TODO make hakase ask others after incorrect message


