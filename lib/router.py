import asyncio
import importlib

from lib.client import client
from lib.responses import misc
from lib.responses import jeopardy
from lib.responses import qtb
from lib.responses import fortune
from lib.responses import note
from lib.responses import weather

importlib.reload(misc)
importlib.reload(jeopardy)
importlib.reload(qtb)

async def list_responses(message,params):
  # Assumes 1 level deep nesting
  list = '```Things I can do:\n'
  for key in response_list:
    for response in response_list[key]:
      if key != 'bare':
        list += '{0}{1}\n'.format(key,response)
      else:
        list += '{}\n'.format(response)
  list += '```'

  await client.send_message(message.channel, list)
  return list

response_list = {
  '>': {
    'avatar': misc.avatar,
    'choose': misc.choose,
    'rand': misc.rand,
    'jeopardy': jeopardy.jeopardy,
    'help': list_responses,
    'qtb': qtb.qtb,
    'getnewgirls': qtb.get_new_girls,
    'fortune': fortune.fortune,
    'note': note.note,
    'weather': weather.weather
  },
  '-':{
    'rand': misc.rand,
    'note': note.note
  },
  'bare': {
    'e': misc.e,
    'ayy': misc.ayy,
    '🐢': misc.turtle,
    'turtle': misc.turtle
  }
}

def parse_message(message):
  return message.split(' ')

def route(key):
  target = False
  key = key.lower()
  if key[0] in response_list and key[1:] in response_list[key[0]]:
    target = response_list[key[0]][key[1:]]
  elif key in response_list['bare']:
    target = response_list['bare'][key]
  return target

async def respond(message):
  params = parse_message(message.content)
  print('Message: {}'.format(message.content))
  print('Params: {}'.format(params))

  function = route(params[0])
  if function:
    await function(message,params[1:])
