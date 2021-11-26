from discord.ext import commands
import logging
import SecretManager
from asyncio import TimeoutError
from main import Attributes
import main as db
import math
from typing import Optional
# import testdb as db

debug_mode = True

research_cache = {}

bot = commands.Bot(command_prefix="?")


@bot.command()
async def join(ctx, name: str, *, must_be_none: Optional[str]):
    if must_be_none is None:
        ctx.send("Sorry, player name must be a single word")
        return
    result = db.new_user(name, ctx.author.id)
    await ctx.send(result[1])
    return

@bot.command()
async def admin(ctx,first:str = None, second:str = None, third:str = None, fourth:str = None, fifth:str = None, sixth:str = None, seventh:str = None):
    discord_id = ctx.author.id
    if discord_id in [262098148283908099,466015764919353346]:
        if first == "tech":
            if second == "create":
                name = third
                cost = int(fourth)
                def check_author(author):
                    def inner_check(message):
                        if message.author.id != ctx.author.id:
                            return False
                        return True

                    return inner_check

                await ctx.send("Please enter the description.")
                description = await bot.wait_for('message', timeout=30.0, check=check_author(ctx.author))
                description = description.content

                bonuses = []

                while True:
                    await ctx.send("Enter a bonus in the form <attribute_name> <value>, or \"exit\" to end.")
                    bonus = await bot.wait_for('message', timeout=30.0, check=check_author(ctx.author))
                    bonus = bonus.content
                    if bonus.lower() == "exit":
                        break
                    else:
                        bonus = bonus.split()
                        bonuses.append((db.get_attribute_id(bonus[0]),bonus[1]))

                prerequisites = []
                while True:
                    await ctx.send("Enter a prerequisite in the form <prerequisite_name> <is_hard=true,false> <cost_bonus> or \"exit\" to end.")
                    prereq = await bot.wait_for('message', timeout=30.0, check=check_author(ctx.author))
                    prereq = prereq.content
                    if prereq.lower() == "exit":
                        break
                    else:
                        prereq = prereq.split()
                        if prereq[1].lower() in ["true","false"]:
                            prerequisites.append((db.get_tech_id(prereq[0]), prereq[1].lower()=="true",int(prereq[2])))
                        else:
                            await ctx.send("Invalid is_hard value.")

                await ctx.send("What should be the cost multiplier for this?")
                multiplier = await bot.wait_for('message', timeout=30.0, check=check_author(ctx.author))
                multiplier = float(multiplier.content)

                output = db.new_tech(name,description,cost,bonuses,prerequisites,multiplier)
                await ctx.send(output[1])
                return
            elif second == "attribute":
                pass
            elif second == "delete":
                pass
    else:
        await ctx.send("You're not an admin. You cannot beat the system. Big bird is watching you.")
        return



@bot.command()
async def info(ctx, name:str, argument:str = None):
    if name is None:
        name = ctx.author.name
    discord_id = None
    discord_id = db.get_user_by_name(name)
    info = db.get_player(discord_id)
    if argument is None:
        output_text = \
            "**"+str(info["display_name"]) + ":**\n" + \
            "Pantheon: " + str(db.get_pantheon_name(info["pantheon"])) + "\n" + \
            "Soldiers: " + str(db.get_army(discord_id)) + "\n"+\
            "Functionaries: " + str(db.get_attribute(discord_id,Attributes.FUNCTIONARIES)) + "\n"+ \
            "Priests: " + str(db.get_attribute(discord_id,Attributes.PRIESTS)) + "\n\n"+ \
            "**Battle statistics:**\n" + \
            "Attack: " + str(db.get_attribute(discord_id,Attributes.ATTACK)) + "\n" + \
            "Defense: " + str(db.get_attribute(discord_id, Attributes.DEFENSE)) + "\n" + \
            "Armor: " + str(db.get_attribute(discord_id, Attributes.ARMOR)) + "\n" + \
            "Initiative: " + str(db.get_attribute(discord_id, Attributes.INITIATIVE)) + "\n\n" + \
            "**Power:**\n" + \
            "Current DP: " + str(db.get_attribute(discord_id,Attributes.POWER)) + "\n"\
            "Income: " + str(db.calculate_income(discord_id)) + "\n"\
            "Remaining Priest Channeling Power: " + str(db.get_attribute(discord_id,Attributes.TOTAL_PRIEST_POWER))
        await ctx.send(output_text)
        return
    elif argument == "income":
        output_text = \
            "**" + str(info["display_name"]) + "\'s income:**\n" + \
            "Total DP: " + str(math.floor(db.get_attribute(discord_id, Attributes.POWER))) + "\n\n" \
            "Income per functional: " + str(db.get_attribute(discord_id,Attributes.INCOME_PER_FUNCTIONAL)) + "\n"\
            "Income per soldier: " + str(db.get_attribute(discord_id, Attributes.INCOME_PER_SOLDIER)) + "\n"\
            "Income per priest: " + str(db.get_attribute(discord_id, Attributes.INCOME_PER_PRIEST)) + "\n"\
            "Base income per turn: " + str(db.get_attribute(discord_id,Attributes.INCOME_PER_FUNCTIONAL)+
                                           db.get_attribute(discord_id, Attributes.INCOME_PER_SOLDIER)+
                                           db.get_attribute(discord_id, Attributes.INCOME_PER_PRIEST))+"\n\n"\
            "Bonus income per functional: " + str(db.get_attribute(discord_id, Attributes.BONUS_POWER_PER_FUNCTIONAL)) + "\n"\
            "Bonus income per soldier: " + str(db.get_attribute(discord_id, Attributes.BONUS_POWER_PER_SOLDIER)) + "\n"\
            "Bonus income per priest: " + str(db.get_attribute(discord_id, Attributes.BONUS_POWER_PER_PRIEST)) + "\n"\
            "Priest income boost: " + str(db.get_attribute(discord_id, Attributes.PRIEST_INCOME_BOOST_RATE)) + \
            " DP for every unit of bonus income, up to a maximum of " + \
            str(db.get_attribute(discord_id,Attributes.PRIEST_INCOME_BOOST_CAPACITY)) + " per priest, or " + \
            str(db.get_attribute(discord_id,Attributes.PRIESTS)* db.get_attribute(discord_id,Attributes.PRIEST_INCOME_BOOST_CAPACITY)) + " total.\n\n" +\
            "Total income per turn: " + str(math.floor(db.calculate_income(discord_id))) + "\n\n" + \
            "Passive population growth rate: " + str(db.get_attribute(discord_id,Attributes.PASSIVE_POPULATION_GROWTH_RATE)*100) + "%/turn"
        await ctx.send(output_text)
        return
    elif argument == "war":
        output_text = "**{name}'s army:**\n" \
            "Soldiers: {soldiers} \n" \
            "Available attackers: {attackers} \n" \
            "Attacks per soldier per turn: {attacks_per_turn} \n\n" \
            "Attack: {attack} \n" \
            "Defense: {defense} \n" \
            "Armor: {armor} \n" \
            "Initiative: {initiative}\n\n"\
            "Soldier cost: {soldier_cost}\n"\
            "Soldier disband cost: {soldier_disband_cost}\n\n"\
            "Functionary defense: {functionary_defense}\n"\
            "Functionary armor: {functionary_armor}\n"\
            .format(
                name=info["display_name"],
                soldiers= int(db.get_attribute(discord_id,Attributes.SOLDIERS)),
                attackers=int(db.get_attribute(discord_id,Attributes.ATTACK_ELIGIBLE_SOLDIERS)),
                attacks_per_turn=db.get_attribute(discord_id,Attributes.ATTACKS_PER_TURN),
                attack=db.get_attribute(discord_id,Attributes.ATTACK),
                defense=db.get_attribute(discord_id, Attributes.DEFENSE),
                armor=db.get_attribute(discord_id,Attributes.ARMOR),
                initiative=db.get_attribute(discord_id,Attributes.INITIATIVE),
                soldier_cost=int(db.get_attribute(discord_id,Attributes.SOLDIER_COST)),
                soldier_disband_cost=int(db.get_attribute(discord_id,Attributes.SOLDIER_DISBAND_COST)),
                functionary_defense=db.get_attribute(discord_id,Attributes.FUNCTIONARY_DEFENSE),
                functionary_armor=db.get_attribute(discord_id,Attributes.FUNCTIONARY_ARMOR)
            )
        await ctx.send(output_text)
        return
    elif argument == "conversion":
        output_text = "**{name}'s conversion metrics:**\n" \
                      "Enemy follower conversion: {enemy_rate:.1%}, {enemy_cost} DP \n" \
                      "Enemy priest conversion: {priest_convert_rate:.1%}, {priest_convert_cost} DP \n" \
                      "Neutral conversion: {neutral_rate:.1%}, {neutral_cost} DP \n\n" \
                      "Priest cost: {priest_cost} \n" \
                      "Max priest channeling per turn: {channeling} \n".format(
            name=info["display_name"],
            enemy_rate=int(db.get_attribute(discord_id, Attributes.ENEMY_CONVERSION_RATE)),
            enemy_cost=int(db.get_attribute(discord_id, Attributes.ENEMY_CONVERSION_COST)),
            priest_convert_rate=db.get_attribute(discord_id, Attributes.ENEMY_PRIEST_CONVERSION_RATE),
            priest_convert_cost=db.get_attribute(discord_id, Attributes.ENEMY_PRIEST_CONVERSION_COST),
            neutral_rate=db.get_attribute(discord_id, Attributes.NEUTRAL_CONVERSION_RATE),
            neutral_cost=db.get_attribute(discord_id, Attributes.NEUTRAL_CONVERSION_COST),
            priest_cost=db.get_attribute(discord_id, Attributes.PRIEST_COST),
            channeling=int(db.get_attribute(discord_id, Attributes.MAXIMUM_PRIEST_CHANNELING))
        )
        await ctx.send(output_text)
        return
    elif argument == "research":
        output_text = "**{name}'s research metrics:**\n" \
                      "Divine inspiration: {inspiration_rate:.1%}, {inspiration_cost} DP/attempt \n" \
                      "Revelation (asleep): {asleep_rate:.1%}, {asleep_cost} DP/attempt \n" \
                      "Revelation (awake): {awake_rate:.1%}, {awake_cost} DP/attempt \n" \
                      "Divine avatar: {avatar_rate:.1%}, {avatar_cost} DP/attempt \n\n" \
                      "Priest research bonus: +{priest_bonus:.0%} \n\n" \
                      "Research cost multiplier (increases proportional to population): {multiplier}".format(
            name=info["display_name"],
            inspiration_rate=int(db.get_attribute(discord_id, Attributes.DIVINE_INSPIRATION_RATE)),
            inspiration_cost=int(db.get_attribute(discord_id, Attributes.DIVINE_INSPIRATION_COST)),
            asleep_rate=db.get_attribute(discord_id, Attributes.ASLEEP_REVELATION_RATE),
            asleep_cost=db.get_attribute(discord_id, Attributes.ASLEEP_REVELATION_COST),
            awake_rate=db.get_attribute(discord_id, Attributes.AWAKE_REVELATION_RATE),
            awake_cost=db.get_attribute(discord_id, Attributes.AWAKE_REVELATION_COST),
            avatar_rate=db.get_attribute(discord_id, Attributes.DIVINE_AVATAR_RATE),
            avatar_cost=int(db.get_attribute(discord_id, Attributes.DIVINE_AVATAR_COST)),
            priest_bonus=db.get_attribute(discord_id, Attributes.PRIEST_RESEARCH_BONUS),
            multiplier=db.get_attribute(discord_id, Attributes.RESEARCH_COST_MULTIPLIER)
        )
        await ctx.send(output_text)
        return
    elif argument == "tech":
        output_text = "**{name}'s tech:**".format(name=info["display_name"])
        for tech_id in db.get_player_techs(discord_id):
            output_text += "\n\n{name}:\n"\
                           "*{description}*".format(name=db.get_tech_name(tech_id),description=db.get_tech_description(tech_id))
        await ctx.send(output_text)
        return
    elif argument == "all":
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
    tech_id = db.get_tech_id(tech_name)
    player_discord = ctx.author.id
    if tech_id is None:
        await ctx.send('Technology "{}" does not exist.'.format(tech_name))
        return
    elif player_discord is None:
        await ctx.send('You have not joined this game yet.')
        return
    else:
        # Phase 1: output text
        success_cost = db.calculate_tech_cost(player_discord, tech_id)
        multiplier = db.get_attribute(player_discord, Attributes.RESEARCH_COST_MULTIPLIER)
        attempt_costs = tuple(map(lambda x: db.get_attribute(player_discord, x) * multiplier, (
            db.Attributes.DIVINE_INSPIRATION_COST,
            db.Attributes.AWAKE_REVELATION_COST,
            db.Attributes.ASLEEP_REVELATION_COST,
            db.Attributes.DIVINE_AVATAR_COST
        )))
        output_text = 'Attempt research of the technology "{tech_name}" (success cost {success_cost}):\n' \
                      ':regional_indicator_a: for divine inspiration (success probability {div_inspr_prob:.1%}, attempt cost {attempt_costs[0]})\n' \
                      ':regional_indicator_b: for waking revelation (success probability {awake_rev_prob:.1%}, attempt cost {attempt_costs[1]})\n' \
                      ':regional_indicator_c: for dream revelation (success probability {dream_rev_prob:.1%}, attempt cost {attempt_costs[2]})\n' \
                      ':regional_indicator_d: to incarnate and command research (success probability {divine_avatar_prob:.1%}, attempt cost {attempt_costs[3]})' \
            .format(tech_name=tech_name,
                    div_inspr_prob=db.get_attribute(player_discord, db.Attributes.DIVINE_INSPIRATION_RATE),
                    awake_rev_prob=db.get_attribute(player_discord, db.Attributes.AWAKE_REVELATION_RATE),
                    dream_rev_prob=db.get_attribute(player_discord, db.Attributes.ASLEEP_REVELATION_RATE),
                    divine_avatar_prob=db.get_attribute(player_discord, db.Attributes.DIVINE_AVATAR_RATE),
                    success_cost=success_cost, attempt_costs=attempt_costs
                    )
        message = await ctx.send(output_text)
        reactions = {
            '\N{REGIONAL INDICATOR SYMBOL LETTER A}': 'divine_inspiration',
            '\N{REGIONAL INDICATOR SYMBOL LETTER B}': 'awake_revelation',
            '\N{REGIONAL INDICATOR SYMBOL LETTER C}': 'asleep_revelation',
            '\N{REGIONAL INDICATOR SYMBOL LETTER D}': 'divine_avatar'
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

            def check_author(author):
                def inner_check(message):
                    if message.author.id != ctx.author.id:
                        return False
                    return True

                return inner_check

            priests = None
            counter = 3
            while priests is None:
                if counter == 0:
                    await ctx.send("Incorrect response too many times. Research aborted.")
                    return
                await ctx.send("Do you wish to use priests for this research? Type yes or no.")
                decision = await bot.wait_for('message', timeout=30.0, check=check_author(ctx.author))
                if decision.content.lower() == 'yes':
                    priests = True
                    break
                elif decision.content.lower() == 'no':
                    priests = False
                    break
                else:
                    await ctx.send("Incorrect response.")
                    counter -= 1

            result_text = db.attempt_research(player_discord, tech_id, reactions[emoji], priests)[1]
            await ctx.send(result_text)
            return
        except TimeoutError:
            ctx.send("Timed out")

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
            ctx.send("Timed out")


def start_bot():
    token = SecretManager.secrets['discord']['clientToken']

    if token is not None and len(token) > 0:
        logging.info("Starting client")
        bot.run(token)
    else:
        logging.error("Could not start: invalid token")


if __name__ == '__main__':
    start_bot()
