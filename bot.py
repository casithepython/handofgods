import asyncio

from discord.ext import commands
import discord
import logging
import SecretManager
from main import Attributes
import main as db
from typing import Optional
import HelpfileReader
import bot_admin
import Attributes

from handofgods.helpers import OneWord

debug_mode = True
PREFIX = "?"


class HandOfGods(commands.Bot):
    def __init__(self, *, command_prefix="?"):
        super().__init__(
            command_prefix=commands.when_mentioned_or(command_prefix)
        )
        self.research_cache = {}
        self.load_extension("handofgods.admin_commands")
        self.load_extension("handofgods.game_commands")


bot = HandOfGods(command_prefix=PREFIX)


@bot.command(alias=['agpl', 'gpl', 'legal'])
async def license(ctx):
    await ctx.reply(
        "This bot is available under the AGPL license, and the source code"
        + "can be found at <https://github.com/casithepython/handofgods>"
    )


@bot.command()
async def version(ctx):
    """Show version info"""
    # @TODO: windows support
    GIT_BIN = "/usr/bin/git"
    try:
        command = [GIT_BIN, "describe", "--dirty"]
        proc = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
    except FileNotFoundError:
        await ctx.reply("Error: Could not find git binary at `{GIT_BIN}`")

    stdout, stderr = await proc.communicate()

    if proc.returncode == 0:
        await ctx.reply(f"`{stdout.decode()}`")
    else:
        command_str = ' '.join(command)
        await ctx.reply(
            f"Error: `{command_str}` returned code {proc.returncode}:\n"
            + f"```\n{stderr.decode()}\n```")


@bot.event
async def on_command_error(context, exception: Exception):
    if isinstance(exception, commands.ConversionError):
        # @TODO: figure out which argument it was
        await context.reply(f"\u26a0 {exception}")
    elif isinstance(exception.__cause__, NotImplementedError):
        await context.reply(f"\u26a0 not implemented")
    # elif isinstace(exception, ...): ...
    else:
        # default handler prints to stderr
        await commands.Bot.on_command_error(bot, context, exception)


@bot.command()
async def whois(ctx, member: discord.Member):
    game_id = db.get_game_id_from_context(ctx)
    name = member.name
    if member.nick:
        name = member.nick
    if db.user_discord_id_exists(member.id, game_id):
        from formatting import pretty_list

        player_ids = db.get_players_by_discord_id(member.id, game_id)
        display_names = map(db.get_display_name, player_ids)
        await ctx.send("{name} plays as {display_names}".format(
            name=name, display_names=pretty_list(display_names)))
    else:
        await ctx.send("{name} has not joined the game".format(name=name))


@bot.command()
async def proxy(ctx, *, text):
    if db.context_grants_admin(ctx):
        await ctx.send(text)
        await ctx.message.delete()


def start_bot():
    token = SecretManager.secrets['discord']['clientToken']

    if token is not None and len(token) > 0:
        logging.info("Starting client")
        bot.run(token)
    else:
        logging.error("Could not start: invalid token")


if __name__ == '__main__':
    start_bot()
