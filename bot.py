from discord.ext import commands
import logging
import SecretManager
from asyncio import TimeoutError
from main import Attributes
import main as db
import math
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
    if must_be_none is None:
        ctx.send("Sorry, player name must be a single word")
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
        else:
            await ctx.send('Admin command does not exist')
    else:
        await ctx.send("You're not an admin. You cannot beat the system. Big bird is watching you.")
        return

@bot.command()
async def info(ctx, name:str, info_type:str = None):
    import formatting
    if name is None:
        name = ctx.author.name

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
            output_text += "\n\n{name}:\n"\
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

@bot.command()
async def research(ctx, *, tech_name):
    import formatting
    from user_interaction import user_react_on_message
    tech_id = db.get_tech_id(tech_name)
    discord_id = ctx.author.id
    if tech_id is None:
        await ctx.send('Technology "{}" does not exist.'.format(tech_name))
        return
    if discord_id is None:
        await ctx.send('You have not joined this game yet.')
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
    
    priest_text = 'Do you wish to use priests for this research? \n'\
        ':regional_indicator_y: Yes\n'\
        ':regional_indicator_n: No'
    use_priests = await user_react_on_message(bot, ctx, priest_text, ctx.author, {
        '\N{REGIONAL INDICATOR SYMBOL LETTER Y}': True,
        '\N{REGIONAL INDICATOR SYMBOL LETTER N}': False
    })
    if use_priests is None:
        await ctx.send("Timed out")
        return
    
    result_text = db.attempt_research(discord_id, tech_id, research_method, use_priests)[1]
    await ctx.send(result_text)

    # ctx.author.id


@bot.command()
async def battle(ctx, player_name: str, quantity: int):
    player_discord = ctx.author.id
    other_player_discord = db.get_user_by_name(player_name)

    expected_outcome = db.expected_damage(player_discord, other_player_discord, quantity)

    if other_player_discord is None:
        await ctx.send('Player "{}" does not exist.'.format(player_name))
        return
    elif player_discord is None:
        await ctx.send('You have not joined this game yet.')
        return
    else:
        # Phase 1: output text
        output_text = 'Attacking {other_player_name} with {quantity} troops).\n' \
                      'Your probability of eliminating all enemy troops is {probability}.' \
                      'The expected damage is {expected_soldiers} soldiers, {expected_functionaries} functionaries' \
                      ', and {expected_priests} priests. The expected troop loss is {expected_loss}.' \
                      'Remember that these probabilities are only estimates.\n' \
                      ':regional_indicator_a: To continue with the battle\n' \
                      ':regional_indicator_b: To cancel the battle'.format(
            other_player_name=player_name, quantity=quantity, probability=expected_outcome[2],
            expected_soldiers=expected_outcome[0][0], expected_functionaries=expected_outcome[0][1],
            expected_priests=expected_outcome[0][2], expected_loss=expected_outcome[1]
        )
        message = await ctx.send(output_text)
        reactions = {
            '\N{REGIONAL INDICATOR SYMBOL LETTER A}': True,
            '\N{REGIONAL INDICATOR SYMBOL LETTER B}': False,
        }
        for reaction in reactions.keys():
            await message.add_reaction(reaction)

        def check(reaction, user):
            if str(reaction.emoji) not in reactions:
                return False
            if user.id != ctx.author.id:
                return False
            if reaction.message.id != message.id:
                return False
            return True

        try:
            user_reaction, _ = await bot.wait_for('reaction_add', timeout=30.0, check=check)
            emoji = str(user_reaction.emoji)

            # wait for reaction from correct player
            for reaction in reactions.keys():
                if reaction != emoji:
                    await message.remove_reaction(reaction, ctx.me)

            if reactions[emoji]:
                results = db.attack(player_discord, other_player_discord, quantity)
                if results[0]:
                    remaining_attackers = db.get_attribute(player_discord, Attributes.ATTACK_ELIGIBLE_SOLDIERS)
                    remaining_soldiers = db.get_attribute(player_discord, Attributes.SOLDIERS)
                    remaining_enemy_soldiers = db.get_attribute(other_player_discord, Attributes.SOLDIERS)

                    result_text = "**Battle results**:\n" \
                                  "Soldiers killed: *{soldiers_killed}*\n" \
                                  "Functionaries killed: *{functionaries_killed}*\n" \
                                  "Priests killed: *{priests_killed}*\n" \
                                  "Enemy troops remaining: *{enemy_troops_remaining}*\n\n" \
                                  "Soldiers lost: *{soldiers_lost}*\n" \
                                  "Soldiers remaining: *{soldiers_remaining}*\n" \
                                  "Attackers remaining: *{attackers_remaining}*".format(
                        soldiers_killed=results[1][0][0], functionaries_killed=results[1][0][1],
                        priests_killed=results[1][0][2], enemy_troops_remaining=remaining_enemy_soldiers,
                        soldiers_lost=results[1][1], soldiers_remaining=remaining_soldiers,
                        attackers_remaining=remaining_attackers
                    )
                    await ctx.send(result_text)
                    return
                elif not results[0]:
                    await ctx.send(results[1])
                    return
                else:
                    await ctx.send("This should not happen")
                    return
            else:
                await ctx.send("Battle canceled.")
                return
        except TimeoutError:
            ctx.send("Timed out")


@bot.command()
async def convert(ctx, quantity: int):
    player_discord = ctx.author.id

    if player_discord is None:
        await ctx.send('You have not joined this game yet.')
        return
    else:
        # Phase 1: output text
        output_text = 'What type of people do you want to convert?\n' \
                      ':regional_indicator_a: Neutrals (Success rate {neutral_success_rate:.1%},' \
                      ' Cost {neutral_cost})\n' \
                      ':regional_indicator_b: Enemy Followers (Success rate {enemy_success_rate:.1%}, ' \
                      'Cost {enemy_cost})\n' \
                      ':regional_indicator_c: Enemy Priests (Success rate {priest_success_rate:.1%},' \
                      ' Cost {priest_cost})\n' \
            .format(neutral_success_rate=db.get_attribute(player_discord, Attributes.NEUTRAL_CONVERSION_RATE),
                    neutral_cost=db.get_attribute(player_discord, Attributes.NEUTRAL_CONVERSION_COST),
                    enemy_success_rate=db.get_attribute(player_discord, Attributes.ENEMY_CONVERSION_RATE),
                    enemy_cost=db.get_attribute(player_discord, Attributes.ENEMY_CONVERSION_COST),
                    priest_success_rate=db.get_attribute(player_discord, Attributes.ENEMY_PRIEST_CONVERSION_RATE),
                    priest_cost=db.get_attribute(player_discord, Attributes.ENEMY_PRIEST_CONVERSION_COST),
                    )

        message = await ctx.send(output_text)
        reactions = {
            '\N{REGIONAL INDICATOR SYMBOL LETTER A}': "neutral",
            '\N{REGIONAL INDICATOR SYMBOL LETTER B}': "enemy",
            '\N{REGIONAL INDICATOR SYMBOL LETTER C}': "enemy_priest",
        }
        for reaction in reactions.keys():
            await message.add_reaction(reaction)

        def check(reaction, user):
            if str(reaction.emoji) not in reactions:
                return False
            if user.id != ctx.author.id:
                return False
            if reaction.message.id != message.id:
                return False
            return True

        try:

            user_reaction, _ = await bot.wait_for('reaction_add', timeout=30.0, check=check)
            emoji = str(user_reaction.emoji)

            # wait for reaction from correct player
            for reaction in reactions.keys():
                if reaction != emoji:
                    await message.remove_reaction(reaction, ctx.me)

            if reactions[emoji] == "neutral":
                results = db.attempt_conversion(player_discord=player_discord,
                                                quantity=quantity,
                                                person_type=reactions[emoji],
                                                other_player_discord=None)
                if results[0]:
                    result_text = "Successfully converted {converts}.".format(converts=results[1])
                elif not results[0]:
                    result_text = results[1]
                else:
                    result_text = "This error should not exist."
                await ctx.send(result_text)
                return
            elif reactions[emoji] in ["enemy", "enemy_priest"]:
                def check_author(author):
                    def inner_check(message):
                        if message.author.id != ctx.author.id:
                            return False
                        return True

                    return inner_check

                await ctx.send("Please specify the player to attempt to convert away from. \n"
                               "Avoid unnecessary whitespaces or characters.")
                other_player_name = await bot.wait_for('message', timeout=30.0, check=check_author(ctx.author))
                other_player_name = other_player_name.content
                results = db.attempt_conversion(player_discord=player_discord,
                                                quantity=quantity,
                                                person_type=reactions[emoji],
                                                other_player_discord=db.get_user_by_name(other_player_name))
                if results[0]:
                    result_text = "Successfully converted {converts}, spending {cost} DP and priest channeling power.".format(
                        converts=results[1][0], cost=results[1][1])
                elif not results[0]:
                    result_text = results[1]
                else:
                    result_text = "This error should not exist."
                await ctx.send(result_text)
                return
            else:
                result_text = "This should never happen"
                await ctx.send(result_text)
                return
        except TimeoutError:
            await ctx.send("Timed out")

@bot.command()
async def help(ctx, *command_context):
    await ctx.send(HelpfileReader.read(PREFIX, command_context))

def start_bot():
    token = SecretManager.secrets['discord']['clientToken']

    if token is not None and len(token) > 0:
        logging.info("Starting client")
        bot.run(token)
    else:
        logging.error("Could not start: invalid token")


if __name__ == '__main__':
    start_bot()
