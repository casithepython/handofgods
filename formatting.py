import main as db
import Attributes

def default_info(info, discord_id):
  return  "> **{display_name}:**\n> " \
          "Pantheon: {pantheon}\n> " + \
          "Soldiers: {soldiers:.0f}\n> " \
          "Functionaries: {functionaries:.0f}\n> " \
          "Priests: \n> \n> " \
          "**Battle statistics:**\n> " \
          "Attack: {attack:.0f}\n> " \
          "Defense: {defense:.0f}\n> " \
          "Armor: {armor:.0f}\n> " \
          "Initiative: {initiative:.0f}\n> \n> " \
          "**Power:**\n> " \
          "Current DP: {power:.0f}\n> " \
          "Income: {income:.0f}\n> " \
          "Remaining Priest Channeling Power: {channel}" \
          .format(
            display_name=info["display_name"],
            pantheon=db.get_pantheon_name(info["pantheon"]),
            soldiers=db.get_army(discord_id),
            functionaries=db.get_attribute(discord_id,Attributes.FUNCTIONARIES),
            priests=db.get_attribute(discord_id,Attributes.PRIESTS),
            attack=db.get_attribute(discord_id,Attributes.ATTACK),
            defense=db.get_attribute(discord_id, Attributes.DEFENSE),
            armor=db.get_attribute(discord_id, Attributes.ARMOR),
            initiative=db.get_attribute(discord_id, Attributes.INITIATIVE),
            power=db.get_attribute(discord_id,Attributes.POWER),
            income=db.calculate_income(discord_id),
            channel=db.calculate_income(discord_id)
          )

def income_info(info, discord_id):
  return  "**{display_name}\'s income:**\n" + \
          "Total DP: {total_dp:.0f}\n\n" \
          "Income per functional: {income_per_functional:.0f}\n"\
          "Income per soldier: {income_per_soldier:.0f}\n"\
          "Income per priest: {income_per_priest:.0f}\n"\
          "Base income per turn: {base_income_per_turn:.0f}\n\n"\
          "Bonus income per functional: {bonus_income_per_functional:.0f}\n"\
          "Bonus income per soldier: {bonus_income_per_soldier:.0f}\n"\
          "Bonus income per priest: {bonus_income_per_priest:.0f}\n"\
          "Priest income boost: {priest_income_boost_rate:.0f}"\
          " DP for every unit of bonus income, up to a maximum of " \
          "{priest_income_boost_capacity:.0f} per priest, or "\
          "{total_boost_capacity:.0f} total.\n\n"\
          "Total income per turn: {total_income_per_turn:.0f}\n\n" + \
          "Passive population growth rate: {pop_growth_rate:.0%}/turn"\
            .format(
              display_name=info["display_name"],
              total_dp=db.get_attribute(discord_id, Attributes.POWER),
              income_per_functional=db.get_attribute(discord_id,Attributes.INCOME_PER_FUNCTIONAL),
              income_per_soldier=db.get_attribute(discord_id, Attributes.INCOME_PER_SOLDIER),
              income_per_priest=db.get_attribute(discord_id, Attributes.INCOME_PER_PRIEST),
              base_income_per_turn=db.get_attribute(discord_id,Attributes.INCOME_PER_FUNCTIONAL) +
                                    db.get_attribute(discord_id, Attributes.INCOME_PER_SOLDIER) +
                                    db.get_attribute(discord_id, Attributes.INCOME_PER_PRIEST),
              bonus_income_per_functional=db.get_attribute(discord_id, Attributes.BONUS_POWER_PER_FUNCTIONAL),
              bonus_income_per_soldier=db.get_attribute(discord_id, Attributes.BONUS_POWER_PER_SOLDIER),
              bonus_income_per_priest=db.get_attribute(discord_id, Attributes.BONUS_POWER_PER_PRIEST),
              priest_income_boost_rate=db.get_attribute(discord_id, Attributes.PRIEST_INCOME_BOOST_RATE),
              priest_income_boost_capacity=db.get_attribute(discord_id,Attributes.PRIEST_INCOME_BOOST_CAPACITY),
              total_boost_capacity=db.get_attribute(discord_id,Attributes.PRIESTS)* db.get_attribute(discord_id,Attributes.PRIEST_INCOME_BOOST_CAPACITY),
              total_income_per_turn=db.calculate_income(discord_id),
              pop_growth_rate=db.get_attribute(discord_id,Attributes.PASSIVE_POPULATION_GROWTH_RATE)
            )

def war_info(info, discord_id):
  return  "**{name}'s army:**\n" \
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


def conversion_info(info, discord_id):
  return  "**{name}'s conversion metrics:**\n" \
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


def research_info(info, discord_id):
  return  "**{name}'s research metrics:**\n" \
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

def request_research_method(tech_name, success_probs, success_cost, attempt_costs):
  return  'Attempt research of the technology "{tech_name}" (success cost {success_cost}):\n' \
          ':regional_indicator_a: for divine inspiration (success probability {success_probs[0]:.1%}, attempt cost {attempt_costs[0]})\n' \
          ':regional_indicator_b: for waking revelation (success probability {success_probs[1]:.1%}, attempt cost {attempt_costs[1]})\n' \
          ':regional_indicator_c: for dream revelation (success probability {success_probs[2]:.1%}, attempt cost {attempt_costs[2]})\n' \
          ':regional_indicator_d: to incarnate and command research (success probability {success_probs[3]:.1%}, attempt cost {attempt_costs[3]})' \
        .format(
          tech_name=tech_name,
          success_probs=success_probs,
          success_cost=success_cost,
          attempt_costs=attempt_costs
        )


def battle_report(soldiers_killed, functionaries_killed, priests_killed, enemy_troops_remaining, soldiers_lost, soldiers_remaining, attackers_remaining):
  return  "**Battle results**:\n" \
          "Soldiers killed: *{soldiers_killed}*\n" \
          "Functionaries killed: *{functionaries_killed}*\n" \
          "Priests killed: *{priests_killed}*\n" \
          "Enemy troops remaining: *{enemy_troops_remaining}*\n\n" \
          "Soldiers lost: *{soldiers_lost}*\n" \
          "Soldiers remaining: *{soldiers_remaining}*\n" \
          "Attackers remaining: *{attackers_remaining}*".format(
            soldiers_killed=soldiers_killed,
            functionaries_killed=functionaries_killed,
            priests_killed=priests_killed,
            enemy_troops_remaining=enemy_troops_remaining,
            soldiers_lost=soldiers_lost,
            soldiers_remaining=soldiers_remaining,
            attackers_remaining=attackers_remaining
          )

def battle_ask_continue(other_player_name, quantity, probability, expected_soldiers, expected_functionaries, expected_priests, expected_loss):
  return 'Attacking {other_player_name} with {quantity} troops).\n' \
                  'Your probability of eliminating all enemy troops is {probability}.' \
                  'The expected damage is {expected_soldiers} soldiers, {expected_functionaries} functionaries' \
                  ', and {expected_priests} priests. The expected troop loss is {expected_loss}.' \
                  'Remember that these probabilities are only estimates.\n' \
                  ':regional_indicator_a: To continue with the battle\n' \
                  ':regional_indicator_b: To cancel the battle'.format(
        other_player_name=other_player_name,
        quantity=quantity,
        probability=probability,
        expected_soldiers=expected_soldiers,
        expected_functionaries=expected_functionaries,
        expected_priests=expected_priests,
        expected_loss=expected_loss
    )

def conversion_target_type(neutral_success_rate, neutral_cost, enemy_success_rate, enemy_cost, priest_success_rate, priest_cost):
  return  'What type of people do you want to convert?\n' \
          ':regional_indicator_a: Neutrals (Success rate {neutral_success_rate:.1%},' \
          ' Cost {neutral_cost})\n' \
          ':regional_indicator_b: Enemy Followers (Success rate {enemy_success_rate:.1%}, ' \
          'Cost {enemy_cost})\n' \
          ':regional_indicator_c: Enemy Priests (Success rate {priest_success_rate:.1%},' \
          ' Cost {priest_cost})\n'.format(
            neutral_success_rate=neutral_success_rate,
            neutral_cost=neutral_cost,
            enemy_success_rate=enemy_success_rate,
            enemy_cost=enemy_cost,
            priest_success_rate=priest_success_rate,
            priest_cost=priest_cost
          )
