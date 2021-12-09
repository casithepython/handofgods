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





@bot.command()
async def info(ctx, name: str = None, info_type: str = None):
    import formatting
    game_id = db.get_game_id_from_context(ctx)
    if name is None:
        output = "> **Current game:**\n> \n> "
        for base_name in db.get_player_names(game_id):
            player_id = db.get_player_by_name(base_name, game_id)
            display_name = db.get_display_name(player_id)
            output += ((
                "**{name}**:\n> "
                + "DP: {power:.0f}\n> "
                + "Functionaries: {fncs:.0f}\n> "
                + "Personal Soldiers: {soldiers:.0f}\n> "
                + "Total Soldiers: {total_soldiers:.0f}\n"
                + "Priests: {priests:.0f}\n> \n> ").format(
                    name=display_name,
                    power=db.get_attribute(player_id, Attributes.POWER),
                    fncs=db.get_attribute(player_id, Attributes.FUNCTIONARIES),
                    soldiers=db.get_attribute(player_id, Attributes.SOLDIERS),
                    total_soldiers=db.get_army(player_id),
                    priests=db.get_attribute(player_id, Attributes.PRIESTS))
            )
        output += "Current turn: {turn:.0f}".format(
            turn=db.current_turn(db.get_game_id_from_context(ctx))
        )
        await ctx.send(output)
        return

    player_id = None
    if name.casefold() == "me":
        player_id = db.get_player_id_from_context(ctx)
    else:
        player_id = db.get_player_by_name(
            name, db.get_game_id_from_context(ctx))

    if player_id is None:
        await ctx.send('Player {name} does not exist'.format(name=name))
        return

    info = db.get_player(player_id)
    if info_type is None:
        output_text = formatting.default_info(info, player_id)
        await ctx.send(output_text)
        return
    elif info_type == "income":
        output_text = formatting.income_info(info, player_id)
        await ctx.send(output_text)
        return
    elif info_type == "war":
        output_text = formatting.war_info(info, player_id)
        await ctx.send(output_text)
        return
    elif info_type == "conversion":
        output_text = formatting.conversion_info(info, player_id)
        await ctx.send(output_text)
        return
    elif info_type == "research":
        output_text = formatting.research_info(info, player_id)
        await ctx.send(output_text)
        return
    elif info_type == "tech":
        output_text = "**{name}'s tech:**".format(name=info["display_name"])
        for tech_id in db.get_player_techs(player_id):
            output_text += (
                "\n> \n> {name}:\n> "
                "*{description}*").format(
                    name=db.get_tech_name(tech_id),
                    description=db.get_tech_description(tech_id))
        await ctx.send(output_text)
        return
    elif info_type == "all":
        await ctx.send("**{name}'s attributes:**".format(
            name=info["display_name"]))
        attributes_per_print = 20  # avoid 2000 character limit
        attributes = db.get_player_attributes(player_id)
        sliced = [
            attributes[i * attributes_per_print:(i + 1) * attributes_per_print]
            for i in range((len(attributes) + attributes_per_print - 1)
                           // attributes_per_print)]
        for sublist in sliced:
            output_text = ""
            for attribute in sublist:
                output_text += "\n{name}: {value}".format(
                    name=attribute[0], value=attribute[1])
            await ctx.send(output_text)

        return


@bot.command()
async def buff(ctx, name: str, attribute: str, amount: int = 1):
    from user_interaction import user_react_on_message
    source_id = db.get_player_id_from_context(ctx)
    target_id = None
    if name == "me":
        target_id = source_id
    else:
        target_id = db.get_player_by_name(
            name, db.get_game_id_from_context(ctx))
    try:
        attribute_id = db.get_attribute_id(attribute)
    except:  # @TODO: what kind of exception?
        #      -> probably IndexError, need to confirm
        await ctx.send("Incorrect attribute.")
        return

    if db.get_army(target_id) > 0:
        cost = db.get_buff_cost(target_id, amount)
        output = f"> You are attempting to buff {attribute} by {amount}." \
                 f"This will cost you {cost} DP.\n> " \
                 f"Do you wish to continue?\n> " \
                 f":thumbsup: Yes\n> " \
                 f":thumbsdown: No"
        do_buff = await user_react_on_message(bot, ctx, output, ctx.author, {
            '\N{THUMBS UP SIGN}': True,
            '\N{THUMBS DOWN SIGN}': False,
        })

        if do_buff:
            results = db.cast_buff(source_id, attribute_id, amount, target_id)
            await ctx.send(results[1])
            return

        else:
            await ctx.send("Canceled.")
            return
    else:
        await ctx.send("The target has no soldiers to buff.")
        return


@bot.command()
async def create(ctx, amount: int, type: str):
    if amount > 0:
        player_id = db.get_player_id_from_context(ctx)
        from user_interaction import user_react_on_message
        if type in ["priests", "priest"]:
            cost = db.get_attribute(player_id, Attributes.PRIEST_COST)
            output = "> You are creating {num:.0f} priests at a cost of " \
                     "{cost:.0f} per priest, for " \
                     "a total of {total:.0f} DP." \
                     "Do you wish to continue?\n> \n> " \
                     ":thumbsup: Yes\n> " \
                     ":thumbsdown: No".format(
                        num=amount,
                        cost=cost,
                        total=amount*cost)

            # @TODO: components?
            do_create = await user_react_on_message(
                bot, ctx, output, ctx.author, {
                    '\N{THUMBS UP SIGN}': True,
                    '\N{THUMBS DOWN SIGN}': False,
                })

            if do_create:
                results = db.recruit_priests(player_id, amount)
                await ctx.send(results[1])
                return

            else:
                await ctx.send("Canceled.")
                return

        elif type in ["soldiers", "soldier", "troops"]:
            cost = db.get_attribute(player_id, Attributes.SOLDIER_COST)
            output = (
                "> You are creating {num:.0f} soldiers at a cost of"
                "{cost:.0f} per soldier, for "
                "a total of {total:.0f} DP."
                "Do you wish to continue?\n> \n> "
                ":thumbsup: Yes\n> "
                ":thumbsdown: No").format(
                    num=amount,
                    cost=cost,
                    total=amount*cost,
                )
            # @TODO: components?
            do_create = await user_react_on_message(
                bot, ctx, output, ctx.author, {
                    '\N{THUMBS UP SIGN}': True,
                    '\N{THUMBS DOWN SIGN}': False,
                })
            if do_create:
                results = db.recruit_soldiers(player_id, amount)
                await ctx.send(results[1])
                return
            else:
                await ctx.send("Canceled.")
                return
        else:
            await ctx.send("Incorrect type.")
            return
    else:
        await ctx.send("> Nice try.")
        return


@bot.command()
async def disband(ctx, amount: int):
    if amount > 0:
        player_id = db.get_player_id_from_context(ctx)
        from user_interaction import user_react_on_message
        cost = db.get_attribute(player_id, Attributes.SOLDIER_DISBAND_COST)
        output = (
            "> You are disbanding {num:.0f} soldiers at a disband cost of "
            "{cost:.0f} per soldier, for a total of {total:.0f} DP."
            "Do you wish to continue?\n> \n> "
            ":thumbsup: Yes\n> "
            ":thumbsdown: No").format(
                num=amount,
                cost=cost,
                total=amount*cost)
        do_disband = await user_react_on_message(
            bot, ctx, output, ctx.author, {
                '\N{THUMBS UP SIGN}': True,
                '\N{THUMBS DOWN SIGN}': False,
            })
        if do_disband:
            results = db.disband_soldiers(player_id, amount)
            await ctx.send(results[1])
            return
        else:
            await ctx.send("> Canceled")
            return
    else:
        await ctx.send("> Nice try.")
        return


@bot.command()
async def research(ctx, *, tech_name):
    import formatting
    from user_interaction import user_react_on_message
    tech_id = db.get_tech_id(tech_name)
    player_id = db.get_player_id_from_context(ctx)
    if tech_id is None:
        await ctx.send('> Technology "{}" does not exist.'.format(tech_name))
        return
    if player_id is None:
        await ctx.send('> You have not joined this game yet.')
        return
    success_cost = db.calculate_tech_cost(player_id, tech_id)
    multiplier = db.get_attribute(
        player_id, Attributes.RESEARCH_COST_MULTIPLIER)
    attempt_costs = tuple(map(
        lambda x: db.get_attribute(player_id, x) * multiplier, (
            Attributes.DIVINE_INSPIRATION_COST,
            Attributes.AWAKE_REVELATION_COST,
            Attributes.ASLEEP_REVELATION_COST,
            Attributes.DIVINE_AVATAR_COST
        )))

    success_probs = tuple(map(
        lambda x: db.get_attribute(player_id, x) * multiplier, (
            Attributes.DIVINE_INSPIRATION_RATE,
            Attributes.AWAKE_REVELATION_RATE,
            Attributes.ASLEEP_REVELATION_RATE,
            Attributes.DIVINE_AVATAR_RATE
        )))

    output_text = formatting.request_research_method(
        tech_name, success_probs, success_cost, attempt_costs)
    research_method = await user_react_on_message(
        bot, ctx, output_text, ctx.author, {
            '\N{REGIONAL INDICATOR SYMBOL LETTER A}': 'divine_inspiration',
            '\N{REGIONAL INDICATOR SYMBOL LETTER B}': 'awake_revelation',
            '\N{REGIONAL INDICATOR SYMBOL LETTER C}': 'asleep_revelation',
            '\N{REGIONAL INDICATOR SYMBOL LETTER D}': 'divine_avatar'
        })
    if research_method is None:
        await ctx.send("Timed out")
        return

    priest_text = '> Do you wish to use priests for this research? \n'\
        '> :regional_indicator_y: Yes\n'\
        '> :regional_indicator_n: No'
    use_priests = await user_react_on_message(
        bot, ctx, priest_text, ctx.author, {
            '\N{REGIONAL INDICATOR SYMBOL LETTER Y}': True,
            '\N{REGIONAL INDICATOR SYMBOL LETTER N}': False
        })
    if use_priests is None:
        await ctx.send("> Timed out")
        return

    result_text = db.attempt_research(player_id, tech_id,
                                      research_method, use_priests)[1]
    await ctx.send(result_text)

    # ctx.author.id


@bot.command()
async def battle(ctx, player_name: str, quantity: int):
    from user_interaction import user_react_on_message
    import formatting

    attacker_id = db.get_player_id_from_context(ctx)
    target_id = db.get_player_by_name(
        player_name, db.get_game_id_from_context(ctx))
    if attacker_id is None:
        await ctx.send('> You have not joined this game yet.')
        return
    if target_id is None:
        await ctx.send('> Player "{}" does not exist.'.format(player_name))
        return

    # expected_outcome = db.expected_damage(attacker_id, target_id, quantity)

    # # Phase 1: output text
    # output_text = formatting.battle_ask_continue(
    #     player_name,
    #     quantity,
    #     expected_outcome[2],
    #     expected_outcome[0][0],
    #     expected_outcome[0][1],
    #     expected_outcome[0][2],
    #     expected_outcome[1]
    # )

    # do_battle = await user_react_on_message(
    #    bot, ctx, output_text, ctx.author, {
    #        '\N{REGIONAL INDICATOR SYMBOL LETTER A}': True,
    #        '\N{REGIONAL INDICATOR SYMBOL LETTER B}': False,
    #    })
    # if do_battle is None:
    #     await ctx.send("> Timed out")
    #     return

    do_battle = True
    if do_battle:
        results = db.attack(attacker_id, target_id, quantity)
        if results[0]:
            remaining_attackers = db.get_attribute(
                attacker_id, Attributes.ATTACK_ELIGIBLE_SOLDIERS)
            remaining_soldiers = db.get_army(attacker_id)
            remaining_enemy_soldiers = db.get_army(target_id)
            result_text = formatting.battle_report(
                results[1][0][0],
                results[1][0][1],
                results[1][0][2],
                remaining_enemy_soldiers,
                results[1][1],
                remaining_soldiers,
                remaining_attackers
            )

            await ctx.send("> " + result_text)
            return
        else:
            await ctx.send("> " + str(results[1]))
            return
    else:
        await ctx.send("> Battle canceled.")
        return


@bot.command()
async def convert(ctx, quantity: int):
    from user_interaction import user_react_on_message
    import formatting
    player_discord = ctx.author.id

    if player_discord is None:
        await ctx.send('> You have not joined this game yet.')
        return

    output_text = formatting.conversion_target_type(
        db.get_attribute(player_discord, Attributes.NEUTRAL_CONVERSION_RATE),
        db.get_attribute(player_discord, Attributes.NEUTRAL_CONVERSION_COST),
        db.get_attribute(player_discord, Attributes.ENEMY_CONVERSION_RATE),
        db.get_attribute(player_discord, Attributes.ENEMY_CONVERSION_COST),
        db.get_attribute(player_discord, Attributes.ENEMY_PRIEST_CONVERSION_RATE),
        db.get_attribute(player_discord, Attributes.ENEMY_PRIEST_CONVERSION_COST)
    )

    conversion_target = await user_react_on_message(bot, ctx, output_text, ctx.author, {
        '\N{REGIONAL INDICATOR SYMBOL LETTER A}': "neutral",
        '\N{REGIONAL INDICATOR SYMBOL LETTER B}': "enemy",
        '\N{REGIONAL INDICATOR SYMBOL LETTER C}': "enemy_priest",
    })

    if conversion_target == "neutral":
        results = db.attempt_conversion(converter_player_id=player_discord,
                                        quantity=quantity,
                                        person_type=conversion_target,
                                        target_player_id=None)
        if results[0]:
            result_text = "> Successfully converted {converts}.".format(converts=results[1])
        else:
            result_text = results[1]
        await ctx.send(result_text)
        return
    elif conversion_target in ["enemy", "enemy_priest"]:
        def check(message):
            return message.author.id == ctx.author.id and db.user_name_exists(message.content)

        await ctx.send("> Please specify the player to attempt to convert away from. \n"
                       "Avoid unnecessary whitespaces or characters.")
        other_player_name = (await bot.wait_for('message', timeout=30.0, check=check)).content
        other_player_id = db.get_player_by_name(other_player_name)

        success, results = db.attempt_conversion(
            converter_player_id=player_discord,
            quantity=quantity,
            person_type=conversion_target,
            target_player_id=other_player_id)

        if success:
            result_text = "> Successfully converted {converts}, spending {cost} DP and priest channeling power.".format(
                converts=results[0], cost=results[1])
        else:
            result_text = results

        await ctx.send(result_text)


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
