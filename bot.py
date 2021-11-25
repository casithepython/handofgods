from discord.ext import commands
import logging
import SecretManager
from asyncio import TimeoutError
from main import Attributes
import main as db

# import testdb as db

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
        # Phase 1: output text
        success_cost = db.calculate_tech_cost(player_id, tech_id)
        multiplier = db.get_research_cost_multiplier(player_id)
        attempt_costs = tuple(map(lambda x: db.get_attribute(player_id, x) * multiplier, (
            db.Attributes.DIVINE_INSPIRATION_COST,
            db.Attributes.AWAKE_REVELATION_COST,
            db.Attributes.ASLEEP_REVELATION_COST,
            db.Attributes.DIVINE_AVATAR_COST
        )))
        output_text = 'Attempt research of the technology "{tech_name}" (success cost {success_cost}):\n' \
                      ':regional_indicator_a: for divine inspiration (success probability {div_inspr_prob:.1%}, attempt cost {attempt_costs[0]})\n' \
                      ':regional_indicator_b: for waking revalation (success probability {awake_rev_prob:.1%}, attempt cost {attempt_costs[1]})\n' \
                      ':regional_indicator_c: for dream revalation (success probability {dream_rev_prob:.1%}, attempt cost {attempt_costs[2]})\n' \
                      ':regional_indicator_d: to incarnate and command research (success probability {divine_avatar_prob:.1%}, attempt cost {attempt_costs[3]})' \
            .format(tech_name=tech_name,
                    div_inspr_prob=db.get_attribute(player_id, db.Attributes.DIVINE_INSPIRATION_RATE),
                    awake_rev_prob=db.get_attribute(player_id, db.Attributes.AWAKE_REVELATION_RATE),
                    dream_rev_prob=db.get_attribute(player_id, db.Attributes.ASLEEP_REVELATION_RATE),
                    divine_avatar_prob=db.get_attribute(player_id, db.Attributes.DIVINE_AVATAR_RATE),
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

            db.attempt_research(player_id, tech_id, reactions[emoji])
        except TimeoutError:
            ctx.send("Timed out")

    # ctx.author.id


@bot.command()
async def battle(ctx, player_name, quantity):
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
                      'Remember that these probabilities are only estimates.' \
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
                    soldiers_killed=results[0][0], functionaries_killed=results[0][1],
                    priests_killed=results[0][2], enemy_troops_remaining=remaining_enemy_soldiers,
                    soldiers_lost=results[1], soldiers_remaining=remaining_soldiers,
                    attackers_remaining=remaining_attackers
                )
                ctx.send(result_text)

        except TimeoutError:
            ctx.send("Timed out")

@bot.command()
async def convert(ctx,):
# @bot.command()
# async def test(ctx):
#   tech_name = "Example Technology"
#   output_text = 'Attempt research of the technology "{tech_name}":\n' \
#     ':regional_indicator_a: for divine inspiration (success probability {div_inspr_prob:.1%})\n'\
#     ':regional_indicator_b: for waking revalation (success probability {awake_rev_prob:.1%})\n'\
#     ':regional_indicator_c: for dream revalation (success probability {dream_rev_prob:.1%})\n'\
#     ':regional_indicator_d: to incarnate and command research (success probability {divine_avatar_prob:.1%})\n'\
#       .format(tech_name=tech_name, div_inspr_prob=0.1,
#             awake_rev_prob=0.2,
#             dream_rev_prob=0.3,
#             divine_avatar_prob=0.4123
#   )
#   message = await ctx.send(output_text)
#   reactions = (
#     '\N{REGIONAL INDICATOR SYMBOL LETTER A}',
#     '\N{REGIONAL INDICATOR SYMBOL LETTER B}',
#     '\N{REGIONAL INDICATOR SYMBOL LETTER C}',
#     '\N{REGIONAL INDICATOR SYMBOL LETTER D}'
#   )
#   for reaction in reactions:
#     await message.add_reaction(reaction)
#   # await ctx.send('Echoing "{}"'.format(echo_message))
#   message = await ctx.send(output_text)
#   reactions = (
#     '\N{REGIONAL INDICATOR SYMBOL LETTER A}',
#     '\N{REGIONAL INDICATOR SYMBOL LETTER B}',
#     '\N{REGIONAL INDICATOR SYMBOL LETTER C}',
#     '\N{REGIONAL INDICATOR SYMBOL LETTER D}'
#   )
#   for reaction in reactions:
#     await message.add_reaction(reaction)

#   def check(reaction, user):
#     if str(reaction.emoji) not in reactions:
#       return False
#     if user.id != ctx.author.id:
#       return False
#     if reaction.message.id != message.id:
#       return False


#   user_reaction, _ = await bot.wait_for('reaction_add', timeout=30.0, check=check)

#   # wait for reaction from correct player
#   for reaction in reactions:
#     if reaction != str(user_reaction.emoji):
#       message.remove_reaction(reaction)


def start_bot():
    token = SecretManager.secrets['discord']['clientToken']

    if token is not None and len(token) > 0:
        logging.info("Starting client")
        bot.run(token)
    else:
        logging.error("Could not start: invalid token")


if __name__ == '__main__':
    start_bot()
