from discord.ext import commands
import logging
import SecretManager

# import main as server

bot = commands.Bot(command_prefix="?")

@bot.command()
async def research(ctx, tech_id):
  pass

@bot.command()
async def attack(ctx, player_name, soldier_count):
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
