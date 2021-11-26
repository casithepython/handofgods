from discord.ext import commands
import logging
import SecretManager
from main import Attributes
import main as db
from typing import Optional
import HelpfileReader
import bot_admin
import Attributes
# import testdb as db

debug_mode = True

research_cache = {}
PREFIX = "?"
bot = commands.Bot(command_prefix=PREFIX)

bot.help_command = None


@bot.command()
async def join(ctx, name: str, *, must_be_none: Optional[str]):
    if must_be_none is not None:
        await ctx.send("Sorry, player name must be a single word")
        return
    result = db.new_user(name, ctx.author.id)
    await ctx.send(result[1])
    return


@bot.command()
async def admin(ctx, *args):
    discord_id = ctx.author.id
    if db.user_is_admin(discord_id):
        if args[0] == 'tech':
            await bot_admin.tech(bot, ctx, *(args[1:]))
        elif args[0] == 'user':
            await bot_admin.user(bot, ctx, *(args[1:]))
        elif args[0] == "newturn":
            await bot_admin.newturn()
        else:
            await ctx.send('Admin command does not exist')
    else:
        await ctx.send("You're not an admin. You cannot beat the system. Big bird is watching you.")
        return


@bot.command()
async def info(ctx, name:str = None, info_type:str = None):
    import formatting
    if name is None:
        output = "> **Current game:**\n> \n> "
        for base_name in db.get_player_names():
            discord = db.get_user_by_name(base_name)
            display_name = db.get_display_name(discord)
            output += "**{name}**:\n> " \
                      "DP: {power:.0f}\n> " \
                      "Functionaries: {funcs:.0f}\n> " \
                      "Soldiers: {soldiers:.0f}\n> " \
                      "Priests: {priests:.0f}\n> \n> ".format(name=display_name,power=db.get_attribute(discord,Attributes.POWER),
                                                      funcs=db.get_attribute(discord,Attributes.FUNCTIONARIES),
                                                      soldiers=db.get_attribute(discord,Attributes.SOLDIERS),
                                                      priests=db.get_attribute(discord,Attributes.PRIESTS))
        output += "Current turn: {turn:.0f}".format(turn=db.current_turn())
        await ctx.send(output)
        return



    discord_id = db.get_user_by_name(name)
    info = db.get_player(discord_id)
    if info_type is None:
        output_text = formatting.default_info(info, discord_id)
        await ctx.send(output_text)
        return
    elif info_type == "income":
        output_text = formatting.income_info(info, discord_id)
        await ctx.send(output_text)
        return
    elif info_type == "war":
        output_text = formatting.war_info(info, discord_id)
        await ctx.send(output_text)
        return
    elif info_type == "conversion":
        output_text = formatting.conversion_info(info, discord_id)
        await ctx.send(output_text)
        return
    elif info_type == "research":
        output_text = formatting.research_info(info, discord_id)
        await ctx.send(output_text)
        return
    elif info_type == "tech":
        output_text = "**{name}'s tech:**".format(name=info["display_name"])
        for tech_id in db.get_player_techs(discord_id):
            output_text += "\n> \n> {name}:\n> "\
                           "*{description}*".format(name=db.get_tech_name(tech_id),description=db.get_tech_description(tech_id))
        await ctx.send(output_text)
        return
    elif info_type == "all":
        await ctx.send("**{name}'s attributes:**".format(name=info["display_name"]))
        attributes_per_print = 20 # avoid 2000 character limit
        attributes = db.get_player_attributes(discord_id)
        sliced = [attributes[i * attributes_per_print:(i + 1) * attributes_per_print] for i in range((len(attributes) + attributes_per_print - 1) // attributes_per_print)]
        for sublist in sliced:
            output_text = ""
            for attribute in sublist:
                output_text += "\n{name}: {value}".format(name=attribute[0],value=attribute[1])
            await ctx.send(output_text)

        return


async def create(ctx,amount:int, type:str):
    if amount > 0:
        discord_id=ctx.author.id
        from user_interaction import user_react_on_message
        if type in ["priests", "priest"]:
            output = "> You are creating {num:.0} priests at a cost of {cost:.0} per priest, for " \
                     "a total of {total} DP." \
                     "Do you wish to continue?\n> \n> " \
                     ":thumbsup: Yes\n> " \
                     ":thumbsdown: No".format(num=amount,cost=db.get_attribute(discord_id,Attributes.PRIEST_COST),
                                              total=amount*db.get_attribute(discord_id,Attributes.PRIEST_COST))
            await ctx.send(output)
            do_create = user_react_on_message(bot, ctx, output, ctx.author, {
                '\N{thumbsup}': True,
                '\N{thumbsdown}': False,
            })
            if do_create:
                results = db.recruit_priests(discord_id,amount)
                await ctx.send(results[1])
                return
            else:
                await ctx.send("Canceled.")
                return

        elif type in ["soldiers", "soldier", "troops"]:
            output = "> You are creating {num:.0} soldiers at a cost of {cost:.0} per soldier, for " \
                     "a total of {total} DP." \
                     "Do you wish to continue?\n> \n> " \
                     ":thumbsup: Yes\n> " \
                     ":thumbsdown: No".format(num=amount, cost=db.get_attribute(discord_id, Attributes.SOLDIER_COST),
                                              total=amount * db.get_attribute(discord_id, Attributes.SOLDIER_COST))
            await ctx.send(output)
            do_create = user_react_on_message(bot, ctx, output, ctx.author, {
                '\N{thumbsup}': True,
                '\N{thumbsdown}': False,
            })
            if do_create:
                results = db.recruit_soldiers(discord_id, amount)
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

async def disband(ctx,amount:int):
    if amount > 0:
        discord_id=ctx.author.id
        from user_interaction import user_react_on_message
        output = "> You are disbanding {num:.0} soldiers at a disband cost of {cost:.0} per soldier, for " \
                 "a total of {total} DP." \
                 "Do you wish to continue?\n> \n> " \
                 ":thumbsup: Yes\n> " \
                 ":thumbsdown: No".format(num=amount, cost=db.get_attribute(discord_id, Attributes.SOLDIER_DISBAND_COST),
                                          total=amount * db.get_attribute(discord_id, Attributes.SOLDIER_DISBAND_COST))
        await ctx.send(output)
        do_create = user_react_on_message(bot, ctx, output, ctx.author, {
            '\N{thumbsup}': True,
            '\N{thumbsdown}': False,
        })
        if do_create:
            results = db.recruit_soldiers(discord_id, amount)
            await ctx.send(results[1])
            return
        else:
            await ctx.send("Canceled.")
            return
    else:
        await ctx.send("> Nice try.")
        return


@bot.command()
async def research(ctx, *, tech_name):
    import formatting
    from user_interaction import user_react_on_message
    tech_id = db.get_tech_id(tech_name)
    discord_id = ctx.author.id
    if tech_id is None:
        await ctx.send('> Technology "{}" does not exist.'.format(tech_name))
        return
    if discord_id is None:
        await ctx.send('> You have not joined this game yet.')
        return
    success_cost = db.calculate_tech_cost(discord_id, tech_id)
    multiplier = db.get_attribute(discord_id, Attributes.RESEARCH_COST_MULTIPLIER)
    attempt_costs = tuple(map(lambda x: db.get_attribute(discord_id, x) * multiplier, (
        Attributes.DIVINE_INSPIRATION_COST,
        Attributes.AWAKE_REVELATION_COST,
        Attributes.ASLEEP_REVELATION_COST,
        Attributes.DIVINE_AVATAR_COST
    )))

    success_probs = tuple(map(lambda x: db.get_attribute(discord_id, x) * multiplier, (
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
    
    result_text = db.attempt_research(discord_id, tech_id, research_method, use_priests)[1]
    await ctx.send(result_text)

    # ctx.author.id


@bot.command()
async def battle(ctx, player_name: str, quantity: int):
    from user_interaction import user_react_on_message
    import formatting

    player_discord = ctx.author.id
    other_player_discord = db.get_user_by_name(player_name)
    if player_discord is None:
        await ctx.send('> You have not joined this game yet.')
        return
    if other_player_discord is None:
        await ctx.send('> Player "{}" does not exist.'.format(player_name))
        return
    
    expected_outcome = db.expected_damage(player_discord, other_player_discord, quantity)

    # Phase 1: output text
    output_text = formatting.battle_ask_continue(
        player_name,
        quantity,
        expected_outcome[2],
        expected_outcome[0][0],
        expected_outcome[0][1],
        expected_outcome[0][2],
        expected_outcome[1]
    )

    do_battle = user_react_on_message(bot, ctx, output_text, ctx.author, {
        '\N{REGIONAL INDICATOR SYMBOL LETTER A}': True,
        '\N{REGIONAL INDICATOR SYMBOL LETTER B}': False,
    })
    if do_battle is None:
        await ctx.send("> Timed out")
        return

    if do_battle:
        results = db.attack(player_discord, other_player_discord, quantity)
        if results[0]:
            remaining_attackers = db.get_attribute(player_discord, Attributes.ATTACK_ELIGIBLE_SOLDIERS)
            remaining_soldiers = db.get_attribute(player_discord, Attributes.SOLDIERS)
            remaining_enemy_soldiers = db.get_attribute(other_player_discord, Attributes.SOLDIERS)
            result_text = formatting.battle_report(
                results[1][0][0],
                results[1][0][1],
                results[1][0][2],
                remaining_enemy_soldiers,
                results[1][1],
                remaining_soldiers,
                remaining_attackers
            )
            
            await ctx.send(">" + result_text)
            return
        else:
            await ctx.send(">" + str(results[1]))
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

    conversion_target = user_react_on_message(bot, ctx, output_text, ctx.author, {
        '\N{REGIONAL INDICATOR SYMBOL LETTER A}': "neutral",
        '\N{REGIONAL INDICATOR SYMBOL LETTER B}': "enemy",
        '\N{REGIONAL INDICATOR SYMBOL LETTER C}': "enemy_priest",
    })

    if conversion_target == "neutral":
        results = db.attempt_conversion(player_discord=player_discord,
                                        quantity=quantity,
                                        person_type=conversion_target,
                                        other_player_discord=None)
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
        other_player_id = db.get_user_by_name(other_player_name)

        success, results = db.attempt_conversion(player_discord=player_discord,
                                        quantity=quantity,
                                        person_type=conversion_target,
                                        other_player_discord=other_player_id)

        if success:
            result_text = "> Successfully converted {converts}, spending {cost} DP and priest channeling power.".format(
                converts=results[0], cost=results[1])
        else:
            result_text = results
        
        await ctx.send(result_text)


@bot.command()
async def help(ctx, *command_context):
    await ctx.send(HelpfileReader.read(PREFIX, command_context))


def start_bot():
    token = SecretManager.secrets['discord']['clientToken']

    if token is not None and len(token) > 0:
        logging.info("Starting client")
        bot.run(token)
    else:
        logging.error("> Could not start: invalid token")


if __name__ == '__main__':
    start_bot()
