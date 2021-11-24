from discord.ext import commands
import logging
import SecretManager
from asyncio import TimeoutError


# import main as db
import testdb as db

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
    # Phase 1: Send message
    success_cost = db.calculate_tech_cost(player_id, tech_id)
    multiplier = db.get_research_cost_multiplier(player_id)
    attempt_costs = tuple(map(lambda x: db.get_attribute(player_id, x) * multiplier, (
      db.Attributes.DIVINE_INSPIRATION_COST,
      db.Attributes.AWAKE_REVELATION_COST,
      db.Attributes.ASLEEP_REVELATION_COST,
      db.Attributes.DIVINE_AVATAR_COST
    )))
    output_text = 'Attempt research of the technology "{tech_name}" (success cost {success_cost}):\n'\
    ':regional_indicator_a: for divine inspiration (success probability {div_inspr_prob:.1%}, attempt cost {attempt_costs[0]})\n'\
    ':regional_indicator_b: for waking revalation (success probability {awake_rev_prob:.1%}, attempt cost {attempt_costs[1]})\n'\
    ':regional_indicator_c: for dream revalation (success probability {dream_rev_prob:.1%}, attempt cost {attempt_costs[2]})\n'\
    ':regional_indicator_d: to incarnate and command research (success probability {divine_avatar_prob:.1%}, attempt cost {attempt_costs[3]})'\
      .format(tech_name=tech_name, div_inspr_prob=db.get_attribute(player_id, db.Attributes.DIVINE_INSPIRATION_RATE),
            awake_rev_prob=db.get_attribute(player_id, db.Attributes.AWAKE_REVELATION_RATE),
            dream_rev_prob=db.get_attribute(player_id, db.Attributes.ASLEEP_REVELATION_RATE),
            divine_avatar_prob=db.get_attribute(player_id, db.Attributes.DIVINE_AVATAR_RATE),
            success_cost=success_cost, attempt_costs=attempt_costs
            )
    message = await ctx.send(output_text)

    # Phase 2: Add reactions
    reactions = {
      '\N{REGIONAL INDICATOR SYMBOL LETTER A}': 'divine_inspiration',
      '\N{REGIONAL INDICATOR SYMBOL LETTER B}': 'awake_revelation',
      '\N{REGIONAL INDICATOR SYMBOL LETTER C}': 'asleep_revelation',
      '\N{REGIONAL INDICATOR SYMBOL LETTER D}': 'divine_avatar'
    }
    for reaction in reactions.keys():
      await message.add_reaction(reaction)


    # Phase 3: Wait for player to react
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

      # Phase 4: Complete the research
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
async def battle(ctx, player_name, soldier_count):
  pass

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
