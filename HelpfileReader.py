import json
from typing import Tuple, Optional

class IncompleteMapper(dict):
  def __missing__(self, key):
    return '{' + key + '}'

with open('help.json', 'r') as f:
  help_document = json.load(f)

def read(prefix:str, command_context: Tuple[str, ...]=(), commands:dict=help_document):
  for command in command_context:
    if 'subcommands' not in commands:
      return "Command help does not exist"
    if command not in commands['subcommands']:
      return "Command help does not exist"
    commands = commands['subcommands'][command]
  output = []
  index = read_index(command_context, commands, force_no_star=True)
  output.append(index)
  
  if 'subcommands' in commands:
    for command_name, command in commands['subcommands'].items():
      output.append(read_index(command_context + (command_name,), command))
  
  return '> ' + '\n> '.join(map(lambda x: x.format(prefix=prefix), filter(lambda x: x, output)))

def read_index(command_context: Optional[Tuple[str, ...]], command: dict, force_no_star:bool=False) -> Optional[str]:
  if 'parameters' not in command:
    command['parameters'] = None
  if 'index' in command:
    return format_command(command_context, command['parameters'], not force_no_star and 'subcommands' in command).format_map(IncompleteMapper({'index':command['index']}))
  else:
    return None

def format_command(command_context, parameters, has_subcommands):
  if command_context is None or len(command_context) == 0:
    return '{index}'
  elif parameters is None:
    return '`{prefix}{command}{star}` {index}'.format_map(IncompleteMapper({'command':' '.join(command_context), 'star':('*' if has_subcommands else '')}))
  else:
    return '`{prefix}{command}{star} {parameters}` {index}'.format_map(IncompleteMapper({
      'command':' '.join(command_context), 'parameters':' '.join(map(lambda x: '<{}>'.format(x), parameters)), 'star':('*' if has_subcommands else '')
    }))
