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

debug_mode = True

research_cache = {}
PREFIX = "?"
bot = commands.Bot(
    command_prefix=commands.when_mentioned_or(PREFIX)
)

bot.help_command = None


@bot.command(alias=['agpl', 'gpl', 'legal'])
async def license(ctx):
    await ctx.send("This bot is available under the AGPL license, and the source code can be found at <https://github.com/casithepython/handofgods>")
    return

@bot.command()
async def join(ctx, name: str, *, must_be_none: Optional[str]):
    if name.casefold() in {'me', 'my'}:
        await ctx.send("Sorry, player name cannot be a special word")
    if must_be_none is not None:
        await ctx.send("Sorry, player name must be a single word")
        return
    result = db.create_player(name, ctx.author.id)
    await ctx.send(result[1])
    return


@bot.command()
async def send(ctx, name:str, amount:int):
    sender_id = db.get_player_id_from_context(ctx)
    receiver_id = db.get_player_by_name(name, db.get_game_id_from_context(ctx))
    results = db.send_power(sender_id, receiver_id, amount)
    await ctx.send(results[1])
    return


@bot.command()
async def pantheon(ctx, first:str, second:str):
    def check_author(author):
        def inner_check(message):
            if message.author.id != author.id:
                return False
            return True
        return inner_check
    player_id = db.get_player_id_from_context(ctx)
    if first == "create":
        if db.player_get_pantheon(player_id) != -1:
            await ctx.send("You must leave your current pantheon before you can create a new one.")
            return
        
        name = second
        await ctx.send("Please enter the description.")
        description = await bot.wait_for('message', timeout=30.0, check=check_author(ctx.author))
        description = description.content
        results = db.create_pantheon(name, description)
        db.join_pantheon(ctx.author.id, db.get_pantheon_by_name(name))
        await ctx.send(results[1])
        return
    elif first == "leave":
        from user_interaction import user_react_on_message
        output = "> Are you sure you want to leave your pantheon?\n> " \
                 ":thumbsup: Yes\n> " \
                 ":thumbsdown: No"
        do_leave = await user_react_on_message(bot, ctx, output, ctx.author, {
            '\N{THUMBS UP SIGN}': True,
            '\N{THUMBS DOWN SIGN}': False,
        })

        if do_leave:
            results = db.leave_pantheon(ctx.author.id)
            await ctx.send(results[1])
            return
        else:
            await ctx.send("Canceled.")
            return


@bot.command()
async def admin(ctx, *args):
    discord_id = ctx.author.id
    if len(args) == 0:
        await ctx.send(HelpfileReader.read(PREFIX, ('admin',)))
        return
    if db.context_grants_admin(ctx):
        if args[0] == 'tech':
            await bot_admin.tech(bot, ctx, *(args[1:]))
        elif args[0] == 'user':
            await bot_admin.user(bot, ctx, *(args[1:]))
        elif args[0] == "newturn":
            await bot_admin.newturn(bot, ctx)
        elif args[0] == 'kill':
            await bot_admin.kill(bot, ctx)
        elif args[0] == 'help':
            await bot_admin.help(bot, ctx, *(args[1:]))
        elif args[0] == 'pantheon':
            await bot_admin.pantheon(bot, ctx, *(args[1:]))
        elif args[0] == 'update':
            await bot_admin.update()
        elif args[0] == 'join':
            await bot_admin.join(bot, ctx, *(args[1:]))
        else:
            await ctx.send('Admin command does not exist')
    else:
        await ctx.send("You're not an admin. You cannot beat the system. Big bird is watching you.")
        return


@bot.command()
async def info(ctx, name:str = None, info_type:str = None):
    import formatting
    game_id = db.get_game_id_from_context(ctx)
    if name is None:
        output = "> **Current game:**\n> \n> "
        for base_name in db.get_player_names(game_id):
            player_id = db.get_player_by_name(base_name, game_id)
            display_name = db.get_display_name(player_id)
            output += "**{name}**:\n> " \
                      "DP: {power:.0f}\n> " \
                      "Functionaries: {funcs:.0f}\n> " \
                      "Personal Soldiers: {soldiers:.0f}\n> " \
                      "Total Soldiers: {total_soldiers:.0f}\n" \
                      "Priests: {priests:.0f}\n> \n> ".format(name=display_name,power=db.get_attribute(player_id, Attributes.POWER),
                                                      funcs=db.get_attribute(player_id, Attributes.FUNCTIONARIES),
                                                      soldiers=db.get_attribute(player_id, Attributes.SOLDIERS),
                                                      total_soldiers=db.get_army(player_id),
                                                      priests=db.get_attribute(player_id, Attributes.PRIESTS))
        output += "Current turn: {turn:.0f}".format(turn=db.current_turn(db.get_game_id_from_context(ctx)))
        await ctx.send(output)
        return

    player_id = None
    if name.casefold() == "me":
        player_id = db.get_player_id_from_context(ctx)
    else:
        player_id = db.get_player_by_name(name, db.get_game_id_from_context(ctx))
    
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
            output_text += "\n> \n> {name}:\n> "\
                           "*{description}*".format(name=db.get_tech_name(tech_id),description=db.get_tech_description(tech_id))
        await ctx.send(output_text)
        return
    elif info_type == "all":
        await ctx.send("**{name}'s attributes:**".format(name=info["display_name"]))
        attributes_per_print = 20 # avoid 2000 character limit
        attributes = db.get_player_attributes(player_id)
        sliced = [attributes[i * attributes_per_print:(i + 1) * attributes_per_print] for i in range((len(attributes) + attributes_per_print - 1) // attributes_per_print)]
        for sublist in sliced:
            output_text = ""
            for attribute in sublist:
                output_text += "\n{name}: {value}".format(name=attribute[0],value=attribute[1])
            await ctx.send(output_text)

        return


@bot.command()
async def buff(ctx,name:str, attribute:str, amount:int = 1):
    from user_interaction import user_react_on_message
    source_id = db.get_player_id_from_context(ctx)
    target_id = None
    if name == "me":
        target_id = source_id
    else:
        target_id = db.get_player_by_name(name, db.get_game_id_from_context(ctx))
    try:
        attribute_id = db.get_attribute_id(attribute)
    except:
        await ctx.send("Incorrect attribute.")
        return

    if db.get_army(target_id) > 0:
        cost = db.get_buff_cost(target_id, amount)
        output = f"> You are attempting to buff {attribute} by {amount}. This will cost you {cost} DP.\n> " \
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
async def create(ctx,amount:int, type:str):
    if amount > 0:
        player_id = db.get_player_id_from_context(ctx)
        from user_interaction import user_react_on_message
        if type in ["priests", "priest"]:
            output = "> You are creating {num:.0f} priests at a cost of {cost:.0f} per priest, for " \
                     "a total of {total:.0f} DP." \
                     "Do you wish to continue?\n> \n> " \
                     ":thumbsup: Yes\n> " \
                     ":thumbsdown: No".format(num=amount,cost=db.get_attribute(player_id,Attributes.PRIEST_COST),
                                              total=amount*db.get_attribute(player_id,Attributes.PRIEST_COST))
            do_create = await user_react_on_message(bot, ctx, output, ctx.author, {
                '\N{THUMBS UP SIGN}': True,
                '\N{THUMBS DOWN SIGN}': False,
            })

            if do_create:
                results = db.recruit_priests(player_id,amount)
                await ctx.send(results[1])
                return

            else:
                await ctx.send("Canceled.")
                return

        elif type in ["soldiers", "soldier", "troops"]:
            output = "> You are creating {num:.0f} soldiers at a cost of {cost:.0f} per soldier, for " \
                     "a total of {total:.0f} DP." \
                     "Do you wish to continue?\n> \n> " \
                     ":thumbsup: Yes\n> " \
                     ":thumbsdown: No".format(num=amount, cost=db.get_attribute(player_id, Attributes.SOLDIER_COST),
                                              total=amount * db.get_attribute(player_id, Attributes.SOLDIER_COST))

            do_create = await user_react_on_message(bot, ctx, output, ctx.author, {
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
async def disband(ctx,amount:int):
    if amount > 0:
        player_id = db.get_player_id_from_context(ctx)
        from user_interaction import user_react_on_message
        output = "> You are disbanding {num:.0f} soldiers at a disband cost of {cost:.0f} per soldier, for " \
                 "a total of {total:.0f} DP." \
                 "Do you wish to continue?\n> \n> " \
                 ":thumbsup: Yes\n> " \
                 ":thumbsdown: No".format(num=amount, cost=db.get_attribute(player_id, Attributes.SOLDIER_DISBAND_COST),
                                          total=amount * db.get_attribute(player_id, Attributes.SOLDIER_DISBAND_COST))
        do_disband = await user_react_on_message(bot, ctx, output, ctx.author, {
            '\N{THUMBS UP SIGN}': True,
            '\N{THUMBS DOWN SIGN}': False,
        })
        if do_disband:
            results = db.disband_soldiers(player_id,amount)
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
    multiplier = db.get_attribute(player_id, Attributes.RESEARCH_COST_MULTIPLIER)
    attempt_costs = tuple(map(lambda x: db.get_attribute(player_id, x) * multiplier, (
        Attributes.DIVINE_INSPIRATION_COST,
        Attributes.AWAKE_REVELATION_COST,
        Attributes.ASLEEP_REVELATION_COST,
        Attributes.DIVINE_AVATAR_COST
    )))

    success_probs = tuple(map(lambda x: db.get_attribute(player_id, x) * multiplier, (
        Attributes.DIVINE_INSPIRATION_RATE,
        Attributes.AWAKE_REVELATION_RATE,
        Attributes.ASLEEP_REVELATION_RATE,
        Attributes.DIVINE_AVATAR_RATE
    )))
    output_text = formatting.request_research_method(tech_name, success_probs, success_cost, attempt_costs)
    research_method = await user_react_on_message(bot, ctx, output_text, ctx.author, {
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
    use_priests = await user_react_on_message(bot, ctx, priest_text, ctx.author, {
        '\N{REGIONAL INDICATOR SYMBOL LETTER Y}': True,
        '\N{REGIONAL INDICATOR SYMBOL LETTER N}': False
    })
    if use_priests is None:
        await ctx.send("> Timed out")
        return
    
    result_text = db.attempt_research(player_id, tech_id, research_method, use_priests)[1]
    await ctx.send(result_text)

    # ctx.author.id


@bot.command()
async def battle(ctx, player_name: str, quantity: int):
    from user_interaction import user_react_on_message
    import formatting

    attacker_id = db.get_player_id_from_context(ctx)
    target_id = db.get_player_by_name(player_name, db.get_game_id_from_context(ctx))
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

    # do_battle = await user_react_on_message(bot, ctx, output_text, ctx.author, {
    #     '\N{REGIONAL INDICATOR SYMBOL LETTER A}': True,
    #     '\N{REGIONAL INDICATOR SYMBOL LETTER B}': False,
    # })
    # if do_battle is None:
    #     await ctx.send("> Timed out")
    #     return

    do_battle = True
    if do_battle:
        results = db.attack(attacker_id, target_id, quantity)
        if results[0]:
            remaining_attackers = db.get_attribute(attacker_id, Attributes.ATTACK_ELIGIBLE_SOLDIERS)
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

        success, results = db.attempt_conversion(converter_player_id=player_discord,
                                        quantity=quantity,
                                        person_type=conversion_target,
                                        target_player_id=other_player_id)

        if success:
            result_text = "> Successfully converted {converts}, spending {cost} DP and priest channeling power.".format(
                converts=results[0], cost=results[1])
        else:
            result_text = results
        
        await ctx.send(result_text)


@bot.command()
async def help(ctx, *command_context):
    await ctx.send(HelpfileReader.read(PREFIX, command_context))

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
        await ctx.send("{name} plays as {display_names}".format(name=name, display_name=pretty_list(display_names)))
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
