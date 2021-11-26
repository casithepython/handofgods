from discord.ext import commands
import logging
import SecretManager
from typing import Optional 
bot = commands.Bot(command_prefix="?")

@bot.command()
async def test(ctx, name:str, *, everything_else: Optional[str]):
  await ctx.send("username is {}".format(name))
  await ctx.send("everything else is `{}`".format(repr(everything_else)))

def start_bot():
    token = SecretManager.secrets['discord']['clientToken']

    if token is not None and len(token) > 0:
        logging.info("Starting client")
        bot.run(token)
    else:
        logging.error("Could not start: invalid token")


if __name__ == '__main__':
    start_bot()
