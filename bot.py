from discord.ext import commands
import logging
import SecretManager

import main as db

debug_mode = True

research_cache = {}

bot = commands.Bot(command_prefix="?")

@bot.command()
async def research(ctx, *, tech_name):
  tech_id = db.get_tech_id(tech_name)
  player_id = db.get_player_id(ctx.author.id)

  if tech_id is None:
    await ctx.send('Technology "{}" does not exist.'.format(tech_name))
    return
  elif player_id is None:
    await ctx.send('You have not joined this game yet.')
    return
  else:
    output_text = 'Attempt research of the technology "{}": react with :regional_indicator_a: for divine inspiration, '.format(tech_name)
    await ctx.send(output_text)
    
    pass
    
  # ctx.author.id

@bot.command()
async def battle(ctx, player_name, soldier_count):
  pass

@bot.command()
async def test(ctx, echo_message):
  await ctx.send('Echoing "{}"'.format(echo_message))


def start_bot():
  token = SecretManager.secrets['discord']['clientToken']

  if token is not None and len(token) > 0:
    logging.info("Starting client")
    bot.run(token)
  else:
    logging.error("Could not start: invalid token")

if __name__ == '__main__':
  start_bot()
