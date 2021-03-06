from lib.client import client
from lib.models import Note

async def note(message,params):
  print(params)
  if len(params) < 1:
    return

  key = params[0]
  note_instance = Note()
  if len(params) < 2:
    found_note = note_instance.find(key)
    if (found_note):
      await message.channel.send(found_note.content)
    else:
      await message.channel.send("Nothing notable found!")
  else:
    note_instance.add(key, ' '.join(params[1:]))
