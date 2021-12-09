import json
import random
import sqlite3

from discord import player
import Attributes

NEVER_EXPIRES = -1
NO_PANTHEON = -1


class connect:
    def __init__(self):
        pass

    def __enter__(self):
        self.__connection = sqlite3.connect("HandOfGods.db")
        self.__connection.row_factory = sqlite3.Row
        self.cursor = self.__connection.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.__connection.commit()
        self.__connection.close()


# ----------------------------------------
# Game management
# ----------------------------------------
def get_game_id_from_context(ctx):
    return ctx.guild.id


def get_maximum_players_from_context(ctx):
    if context_grants_admin(ctx):
        return 100
    else:
        return 1


def get_player_count_from_context(ctx):
    with connect() as cursor:
        cursor.execute("SELECT SUM(1) AS count FROM players WHERE discord_id = ? AND game_id = ?",
                       (ctx.author.id, get_game_id_from_context(ctx)))
        return cursor.fetchone()[0]


# ----------------------------------------
# User management
# ----------------------------------------
def player_get_game(player_id):
    with connect() as cursor:
        cursor.execute("SELECT game_id FROM players WHERE id = ?", (player_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        else:
            return row[0]


def get_player_id_from_context(ctx):
    with connect() as cursor:
        cursor.execute(
            "SELECT id FROM players WHERE discord_id = ? AND game_id = ?",
            (ctx.author.id, get_game_id_from_context(ctx)))
        row = cursor.fetchone()
        if row is None:
            return None
        else:
            return row[0]


def user_name_exists(name, game_id):
    with connect() as cursor:
        cursor.execute("SELECT 1 FROM players WHERE name = ? AND game_id = ?", (name.casefold(), game_id))
        return cursor.fetchone() is not None


def get_player_by_name(name, game_id):
    with connect() as cursor:
        cursor.execute("SELECT id FROM players WHERE name = ? AND game_id = ?", (name.casefold(), game_id))
        row = cursor.fetchone()
        if row is None:
            return None
        else:
            return row[0]


def get_players_by_discord_id(discord_id, game_id):
    with connect() as cursor:
        cursor.execute("SELECT id FROM players WHERE discord_id = ? AND game_id = ?", (discord_id, game_id))
        return [row[0] for row in cursor.fetchall()]


def player_id_exists(player_id):
    with connect() as cursor:
        cursor.execute("SELECT 1 FROM players WHERE id = ?", (player_id,))
        return cursor.fetchone() is not None


def user_discord_id_exists(discord_id, game_id):
    with connect() as cursor:
        cursor.execute("SELECT 1 FROM players WHERE discord_id = ? AND game_id = ?", (discord_id, game_id))
        return cursor.fetchone() is not None


def create_player(name, ctx, ignore_max_players=False):
    discord_id = ctx.author.id
    game_id = get_game_id_from_context(ctx)

    user_max_players = get_maximum_players_from_context(ctx)
    if ignore_max_players or user_max_players <= get_player_id_from_context(ctx):
        return False, "You have used up all of your player slots in this game (you have {})".format(user_max_players)
    if user_name_exists(name, game_id):
        return False, "A player has already taken that name"

    with connect() as cursor:
        cursor.execute(
            'INSERT INTO players (name, display_name, discord_id, game_id) VALUES (?,?,?,?)',
            (name.casefold(), name, discord_id, game_id))
        player_id = cursor.lastrowid
        defaults = {
            Attributes.ATTACK: 0,
            Attributes.DEFENSE: 0,
            Attributes.INITIATIVE: 0,
            Attributes.ARMOR: 1,
            Attributes.RESEARCH_COST_MULTIPLIER: 1,
            Attributes.DIVINE_INSPIRATION_RATE: 0.05,
            Attributes.DIVINE_INSPIRATION_COST: 2,
            Attributes.AWAKE_REVELATION_RATE: 0.2,
            Attributes.AWAKE_REVELATION_COST: 10,
            Attributes.ASLEEP_REVELATION_RATE: 0.1,
            Attributes.ASLEEP_REVELATION_COST: 5,
            Attributes.DIVINE_AVATAR_RATE: 1,
            Attributes.DIVINE_AVATAR_COST: 20,
            Attributes.PRIEST_RESEARCH_BONUS: 0.3,
            Attributes.PASSIVE_POPULATION_GROWTH_RATE: 0.13,
            Attributes.INCOME_PER_FUNCTIONAL: 1,
            Attributes.INCOME_PER_SOLDIER: 0,
            Attributes.INCOME_PER_PRIEST: 0,
            Attributes.BONUS_POWER_PER_FUNCTIONAL: 1,
            Attributes.PRIEST_INCOME_BOOST_CAPACITY: 5,
            Attributes.ENEMY_CONVERSION_RATE: 0.1,
            Attributes.ENEMY_CONVERSION_COST: 2,
            Attributes.NEUTRAL_CONVERSION_RATE: 0.2,
            Attributes.NEUTRAL_CONVERSION_COST: 1,
            Attributes.ENEMY_PRIEST_CONVERSION_RATE: 0.05,
            Attributes.ENEMY_PRIEST_CONVERSION_COST: 50,
            Attributes.PANTHEON_BONUS_MULTIPLIER: 0.5,
            Attributes.MAXIMUM_PRIEST_CHANNELING: 10,
            Attributes.PRIEST_COST: 15,
            Attributes.SOLDIER_COST: 0,
            Attributes.SOLDIER_DISBAND_COST: 0,
            Attributes.PRIESTS: 0,
            Attributes.SOLDIERS: 0,
            Attributes.FUNCTIONARIES: 1000,
            Attributes.POWER: 1000,
            Attributes.TOTAL_CONVERTED: 0,
            Attributes.TOTAL_POACHED: 0,
            Attributes.TOTAL_DESTROYED: 0,
            Attributes.TOTAL_LOST: 0,
            Attributes.TOTAL_MASSACRED: 0,
            Attributes.TOTAL_POPULATION_LOST: 0,
            Attributes.TOTAL_SPENT: 0,
            Attributes.TOTAL_INCOME: 0,
            Attributes.BONUS_POWER_PER_SOLDIER: 0,
            Attributes.BONUS_POWER_PER_PRIEST: 0,
            Attributes.ATTACKS_PER_TURN: 1,
            Attributes.FUNCTIONARY_ARMOR: 1,
            Attributes.FUNCTIONARY_DEFENSE: 0,
            Attributes.ATTACK_ELIGIBLE_SOLDIERS: 0,
            Attributes.TOTAL_PRIEST_POWER: 0,
            Attributes.PRIEST_INCOME_BOOST_RATE: 5,
            Attributes.DP_BUFF_POINTS: 0,
            Attributes.DP_BUFF_COST_MULTIPLIER: 0.01
        }
        for attribute_id, value in defaults.items():
            __insert_attribute(cursor, player_id, attribute_id, value, 0, NEVER_EXPIRES)
    return True, "Successfully added user " + name


def user_delete(player_id):
    with connect() as cursor:
        cursor.execute('DELETE FROM players WHERE id = ?', (player_id,))
        cursor.execute('DELETE FROM player_attributes WHERE player_id = ?', (player_id,))
        cursor.execute('DELETE FROM player_technologies WHERE player_id = ?', (player_id,))
        pass


def get_player(player_id):
    info = get_player_info(player_id)
    return {"id": info["id"],
            "name": info["name"],
            "display_name": info['display_name'],
            "discord_id": info['discord_id'],
            "pantheon": info['pantheon'],
            "tech": get_player_techs(player_id),
            "attributes": get_player_attributes(player_id)}


def get_player_attributes(player_id):
    ids = []
    with connect() as cursor:
        cursor.execute("SELECT id FROM attributes")
        ids.extend(map(lambda x: x[0], cursor.fetchall()))
    return [(get_attribute_name(attribute_id), get_attribute(player_id, attribute_id)) for attribute_id in ids]


def get_player_info(player_id):
    info = []
    with connect() as cursor:
        cursor.execute("SELECT * FROM players WHERE id = ?", (player_id,))
        for value in cursor.fetchone():
            info.append(value)
    return info


def get_player_ids(game_id):
    player_ids = []
    with connect() as cursor:
        cursor.execute("SELECT id FROM players WHERE game_id = ?", (game_id,))
        player_ids = [row['id'] for row in cursor.fetchall()]
    return player_ids


def get_player_names(game_id):
    names = None
    with connect() as cursor:
        cursor.execute("SELECT name FROM players WHERE game_id = ?", (game_id,))
        names = [row['name'] for row in cursor.fetchall()]
    return names


def get_display_name(player_id):
    display_name = None
    with connect() as cursor:
        cursor.execute("SELECT display_name FROM players WHERE id = ?", (player_id,))
        display_name = cursor.fetchone()[0]
    return display_name


def context_grants_admin(ctx):
    return ctx.author.id in (262098148283908099, 466015764919353346)


def get_research_cost_multiplier(player_id):
    return get_attribute(player_id, Attributes.RESEARCH_COST_MULTIPLIER)


# ----------------------------------------
# Power
# ----------------------------------------

def get_power(player_id):
    return get_attribute(player_id, Attributes.POWER)


def give_power(player_id, power):
    turn = current_turn(player_get_game(player_id))
    with connect() as cursor:
        cursor.execute(
            "INSERT INTO player_attributes (player_id,attribute_id,value,start_turn,expiry_turn) VALUES (?,?,?,?,?)",
            (player_id, Attributes.POWER, power, turn, NEVER_EXPIRES))


def spend_power(player_id, power):
    player_power = get_power(player_id)
    if power <= player_power:
        give_power(player_id, -power)
        return True
    else:
        return False


def has_sufficient_channeling_power(player_id, amount):
    return amount <= get_attribute(player_id, Attributes.TOTAL_PRIEST_POWER)


def get_channeling_power(player_id):
    return get_attribute(player_id, Attributes.TOTAL_PRIEST_POWER)


def spend_channeling_power(player_id, amount):
    turn = current_turn(player_get_game(player_id))
    insert_attribute(player_id, Attributes.TOTAL_PRIEST_POWER, -amount, turn, turn)


# ----------------------------------------
# Attributes
# ----------------------------------------
def get_attribute_id(name):
    attribute_id = None
    with connect() as cursor:
        cursor.execute("SELECT id FROM attributes WHERE name = ?", (name.lower(),))
        attribute_id = cursor.fetchone()[0]
    return attribute_id


def insert_attribute(player_id, attribute_id, value, start_turn, expiry_turn):
    with connect() as cursor:
        __insert_attribute(cursor, player_id, attribute_id, value, start_turn, expiry_turn)


def __insert_attribute(cursor, player_id, attribute_id, value, start_turn, expiry_turn):
    cursor.execute(
        "INSERT INTO player_attributes (player_id, attribute_id, value,start_turn,expiry_turn) "
        "VALUES (?,?,?,?,?)",
        (player_id, attribute_id, value, start_turn, expiry_turn))


def increase_attribute(player_id, attribute_id, value, expiry_turn):
    insert_attribute(player_id, attribute_id, value, current_turn(player_get_game(player_id)), expiry_turn)


def get_attribute(player_id, attribute_id, turn=None):
    pantheon = get_player_pantheon(player_id)
    my_value = None
    if turn is None:
        turn = current_turn(player_get_game(player_id))
    with connect() as cursor:
        cursor.execute(
            "SELECT SUM(value) FROM player_attributes WHERE player_id=? AND attribute_id=? AND (expiry_turn=-1 OR "
            "expiry_turn >= ?) AND start_turn<=?",
            (player_id, attribute_id, turn, turn))
        my_value = cursor.fetchone()[0]
    if pantheon == -1 or attribute_id == Attributes.PANTHEON_BONUS_MULTIPLIER:  # can't have infinite recursion
        return my_value
    else:
        values = []
        players = []
        with connect() as cursor:
            cursor.execute("SELECT player_id FROM players WHERE pantheon = ?", (pantheon,))
            for item in cursor.fetchall():
                players.append(item[0])
        for player in players:
            if turn is None:
                turn = current_turn(player_get_game(player_id))
            with connect() as cursor:
                cursor.execute(
                    "SELECT SUM(value) FROM player_attributes "
                    "WHERE player_id=? AND attribute_id=? AND (expiry_turn=-1 OR "
                    "expiry_turn >= ?) AND start_turn<=?",
                    (player, attribute_id, turn, turn))
                temp_value = cursor.fetchone()[0]
            values.append(temp_value)
        if attribute_id in {Attributes.ATTACK, Attributes.DEFENSE, Attributes.INITIATIVE, Attributes.ARMOR}:
            return max(values)
        else:
            return max(my_value, max(values)*get_attribute(player_id, Attributes.PANTHEON_BONUS_MULTIPLIER))


def get_attribute_name(attribute_id):
    name = None
    with connect() as cursor:
        cursor.execute(
            "SELECT display_name FROM attributes WHERE id = ?",
            (attribute_id,))
        name = cursor.fetchone()[0]
    return name


def get_num_attributes():
    num = None
    with connect() as cursor:
        cursor.execute("SELECT id FROM attributes")

        num = len(cursor.fetchall())
    return num


def attribute_exists(attribute_id):
    with connect() as cursor:
        cursor.execute(
            "SELECT 1 FROM attributes WHERE id = ?",
            (attribute_id,))
        return cursor.fetchone() is not None


# ----------------------------------------
# Tech
# ----------------------------------------
def tech_name_exists(name):
    with connect() as cursor:
        cursor.execute("SELECT 1 FROM technologies WHERE name = ?", (name.casefold(),))
        return cursor.fetchone() is not None


def tech_exists(tech_id):
    with connect() as cursor:
        cursor.execute("SELECT 1 FROM technologies WHERE id = ?", (tech_id,))
        return cursor.fetchone() is not None


def new_tech(
    name, description, cost, bonuses=[],
    prerequisites=[], chance_multiplier=1
):
    # bonuses should be formatted as [[tech_1_id,value1],[tech_2_id,value2]]
    if bonuses is None:
        bonuses = []

    if not tech_name_exists(name):
        with connect() as cursor:
            cursor.execute(
                "INSERT INTO technologies (name,display_name,description,cost,chance_multiplier) VALUES (?,?,?,?,?)",
                (name.casefold(), name, description, cost, chance_multiplier))
            cursor.execute("SELECT id FROM technologies WHERE name = ?", (name.casefold(),))
            tech_id = cursor.fetchone()[0]
            for bonus in bonuses:
                cursor.execute("INSERT INTO tech_bonuses (tech_id,attribute_id,value) VALUES (?,?,?)",
                               (tech_id, bonus[0], bonus[1]))
        for prereq in prerequisites:
            add_tech_prerequisite(tech_id, prereq[0], prereq[1] is True, prereq[2])
        return True, "Successfully created."
    else:
        return False, "Already exists."


def add_tech_bonus(tech_id, attribute_id, value):
    if tech_exists(tech_id):
        with connect() as cursor:
            cursor.execute("INSERT INTO tech_bonuses (tech_id, attribute_id, value) values (?,?,?)",
                           (tech_id, attribute_id, value))
        return True
    else:
        return False


def clear_tech_bonuses(tech_id, attribute_id):
    with connect() as cursor:
        cursor.execute("DELETE FROM tech_bonuses WHERE tech_id = ? AND attribute_id = ?", (tech_id, attribute_id))


def add_tech_prerequisite(tech_id, prerequisite_id, is_hard, cost_bonus):
    with connect() as cursor:
        cursor.execute("INSERT INTO tech_prerequisites (tech_id, prerequisite_id, is_hard, cost_bonus) VALUES "
                       "(?,?,?,?)", (tech_id, prerequisite_id, is_hard, cost_bonus))


def get_tech_prerequisites(tech_id):
    prerequisites = []
    with connect() as cursor:
        cursor.execute("SELECT prerequisite_id,is_hard,cost_bonus FROM tech_prerequisites WHERE tech_id = ?",
                       (tech_id,))
        for prerequisite in json.loads(cursor.fetchall()[0][0]):
            prerequisites.append(prerequisite)
    return prerequisites


def get_hard_prerequisites(tech_id):
    prerequisites = []
    with connect() as cursor:
        prerequisites = [prerequisite[0] for prerequisite in
                         cursor.execute("SELECT prerequisite_id from tech_prerequisites WHERE id = ? AND is_hard = 1",
                                        (tech_id,))]
    return prerequisites


def get_tech_id(name):
    tech_id = None
    with connect() as cursor:
        cursor.execute("SELECT id FROM technologies WHERE name = ?", (name.casefold(),))
        tech_id = cursor.fetchone()[0]
    return tech_id


def get_tech_description(tech_id):
    description = None
    with connect() as cursor:
        cursor.execute("SELECT description from technologies WHERE id = ?", (tech_id,))
        description = cursor.fetchone()[0]
    return description


def get_tech_name(tech_id):
    name = None
    with connect() as cursor:
        cursor.execute("SELECT display_name from technologies WHERE id = ?", (tech_id,))
        name = cursor.fetchone()[0]
    return name


def get_tech_cost(tech_id):
    cost = None
    with connect() as cursor:
        cursor.execute("SELECT cost from technologies WHERE id = ?", (tech_id,))
        cost = cursor.fetchone()[0]
    return cost


def get_tech_names():
    names = []
    with connect() as cursor:
        names = [name[0] for name in cursor.execute("SELECT name FROM technologies")]
    return names


def get_tech_chance_multiplier(tech_id):
    multiplier = None
    with connect() as cursor:
        cursor.execute("SELECT chance_multiplier FROM technologies WHERE id = ?", (tech_id,))
        multiplier = cursor.fetchone()[0]
    return multiplier


def get_player_techs(player_id):
    techs = []
    with connect() as cursor:
        cursor.execute("SELECT technology_id FROM player_technologies WHERE player_id = ?", (player_id,))
        techs = list(map(lambda x: x[0], cursor.fetchall()))
    return techs


def player_has_tech(player_id, tech_id):
    with connect() as cursor:
        cursor.execute("SELECT 1 FROM player_technologies WHERE player_id = ? AND technology_id = ?",
                       (player_id, tech_id))
        return cursor.fetchone() is not None


def check_prerequisites(player_id, tech_id):
    required_prerequisites = []
    for prerequisite in get_hard_prerequisites(tech_id):
        if not player_has_tech(player_id, prerequisite):
            required_prerequisites.append(prerequisite)

    return len(required_prerequisites) == 0, required_prerequisites


def technology_get_prerequisites(technology_id):
    with connect() as cursor:
        cursor.execute("SELECT prerequisite_id FROM tech_prerequisites WHERE tech_id = ?", (technology_id,))
        return [row[0] for row in cursor.fetchall()]


def technologies_get_prereq_display_info(technology_id):
    prereq_ids = technology_get_prerequisites(technology_id)
    with connect() as cursor:
        cursor.execute(
            "SELECT prerequisite_id, is_hard, cost_bonus FROM tech_prerequisites WHERE tech_id = ?",
            (technology_id,))
        rows = ((row[0], row[1], row[2]) for row in cursor.fetchall())
        prereq_ids, is_hard, cost_bonus = zip(*rows)
        cursor.execute(
            "SELECT name FROM technologies WHERE id in ({questionmarks})".format(
                questionmarks=','.join('?' * len(prereq_ids))), tuple(prereq_ids))
        names = [row[0] for row in cursor.fetchall()]

        return zip(prereq_ids, names, is_hard, cost_bonus)


# ----------------------------------------
# Research
# ----------------------------------------
def attempt_research(player_id, tech_id, method, priest=False):
    if not tech_exists(tech_id):
        return False, "This technology does not exist."
    if player_has_tech(player_id, tech_id):
        return False, "You have already researched this technology."
    prerequisites = technology_get_prerequisites(tech_id)
    total_bonus = 0
    prereq_pass = True
    hard_fails = []
    for id, name, hard, bonus in prerequisites:
        if player_has_tech(player_id, id):
            total_bonus += bonus
        elif hard:
            prereq_pass = False
            hard_fails.append(name)
    if not prereq_pass:
        tech_list = ""
        if len(hard_fails) > 1:
            tech_list = ", ".join(hard_fails[:-1]) + " and " + hard_fails[-1]
        else:
            tech_list = hard_fails[0]
        return False, (
            "You have not researched all the needed technologies."
            "You must research {} before researching this technology".format(tech_list))

    if method == "divine_inspiration":
        attribute_rate = get_attribute(player_id, Attributes.DIVINE_INSPIRATION_RATE)
        attribute_cost = get_attribute(player_id, Attributes.DIVINE_INSPIRATION_COST)
    elif method == "awake_revelation":
        attribute_rate = get_attribute(player_id, Attributes.AWAKE_REVELATION_RATE)
        attribute_cost = get_attribute(player_id, Attributes.AWAKE_REVELATION_COST)
    elif method == "asleep_revelation":
        attribute_rate = get_attribute(player_id, Attributes.ASLEEP_REVELATION_RATE)
        attribute_cost = get_attribute(player_id, Attributes.ASLEEP_REVELATION_COST)
    elif method == "divine_avatar":
        attribute_rate = get_attribute(player_id, Attributes.DIVINE_AVATAR_RATE)
        attribute_cost = get_attribute(player_id, Attributes.DIVINE_AVATAR_COST)
    else:
        return False, "Invalid research method."

    success_cost = max(0, calculate_tech_cost(player_id, tech_id) + total_bonus)
    attempt_cost = attribute_cost * get_research_cost_multiplier(player_id)

    priest_used = False
    if priest:
        if has_sufficient_channeling_power(player_id, attempt_cost + success_cost):
            attribute_rate += get_attribute(player_id, Attributes.PRIEST_RESEARCH_BONUS)
            priest_used = True

    if get_power(player_id) >= attempt_cost + success_cost:
        spend_power(player_id, attempt_cost)
        if priest_used:
            spend_channeling_power(player_id, attempt_cost)
        if random.random() <= attribute_rate:
            complete_research(player_id, tech_id)
            spend_power(player_id, success_cost)
            if priest_used:
                spend_channeling_power(player_id, success_cost)
            return True, "Successfully researched " + get_tech_name(tech_id) + "."
        else:
            return False, "Failed research chance, " + str(attempt_cost) + " DP spent."
    else:
        return False, "You do not have enough DP to attempt this research."


def calculate_tech_cost(player_id, tech_id):
    base_cost = get_tech_cost(tech_id)
    player_cost_multiplier = get_attribute(player_id, Attributes.RESEARCH_COST_MULTIPLIER)
    return base_cost * player_cost_multiplier


def player_has_technology(player_id, technology_id, turn=None):
    if turn is None:
        turn = current_turn(player_get_game(player_id))
    with connect() as cursor:
        cursor.execute(
            "SELECT 1 FROM player_technologies WHERE player_id = ? AND technology_id = ? AND start_turn <= ?",
            (player_id, technology_id, turn))
        return cursor.fetchone() is not None


def complete_research(player_id, tech_id):
    if not tech_exists(tech_id):
        return False
    if not player_has_technology(player_id, tech_id):
        with connect() as cursor:
            turn = current_turn(player_get_game(player_id))
            cursor.execute("INSERT INTO player_technologies (player_id, technology_id, start_turn) VALUES (?, ?, ?)",
                           (player_id, tech_id, turn + 1))

            # Apply bonuses
            cursor.execute("SELECT attribute_id,value FROM tech_bonuses WHERE tech_id = ?", (tech_id,))
            turn = current_turn(player_get_game(player_id))
            for bonus in cursor.fetchall():
                attribute, value = tuple(bonus)

                cursor.execute(
                    "INSERT INTO player_attributes (player_id,attribute_id,value,start_turn,expiry_turn) values ("
                    "?,?,?,?,?)",
                    (player_id, attribute, value, current_turn(player_get_game(player_id)), NEVER_EXPIRES))
            return True
    else:
        return False


# ----------------------------------------
# Turns
# ----------------------------------------
def current_turn(game_id):
    turn = None
    with connect() as cursor:
        cursor.execute("SELECT value FROM system_variables WHERE name = ? AND game_id = ?", ("turn", game_id))
        turn = cursor.fetchone()[0]
    return int(turn)


def calculate_income(player_id):
    population_bonus_power = \
        get_attribute(player_id, Attributes.BONUS_POWER_PER_FUNCTIONAL) + \
        get_attribute(player_id, Attributes.BONUS_POWER_PER_SOLDIER) + \
        get_attribute(player_id, Attributes.BONUS_POWER_PER_PRIEST)

    boost_capacity_priest = get_attribute(player_id, Attributes.PRIEST_INCOME_BOOST_CAPACITY)
    boost_capacity = get_attribute(player_id, Attributes.PRIESTS) * boost_capacity_priest
    income_boost = get_attribute(player_id, Attributes.PRIEST_INCOME_BOOST_RATE) \
        * min(population_bonus_power, boost_capacity)

    # Base income
    base_income = \
        (get_attribute(player_id, Attributes.FUNCTIONARIES)
            * get_attribute(player_id, Attributes.INCOME_PER_FUNCTIONAL)) \
        + (get_attribute(player_id, Attributes.SOLDIERS)
            * get_attribute(player_id, Attributes.INCOME_PER_SOLDIER)) \
        + (get_attribute(player_id, Attributes.PRIESTS)
            * get_attribute(player_id, Attributes.INCOME_PER_PRIEST))

    return income_boost+base_income


def new_turn(game_id):
    # Increase turn counter
    turn = current_turn(game_id) + 1
    with connect() as cursor:
        cursor.execute("UPDATE system_variables SET value = ? WHERE name = ? AND game_id = ?", (turn, "turn", game_id))

    for player_id in get_player_ids(game_id):
        # Grow population
        growth_amount = get_attribute(player_id, Attributes.FUNCTIONARIES) \
            * get_attribute(player_id, Attributes.PASSIVE_POPULATION_GROWTH_RATE)
        insert_attribute(player_id, Attributes.FUNCTIONARIES, growth_amount, turn, NEVER_EXPIRES)

        # Check for and add income
        # Population bonus power
        give_power(player_id, calculate_income(player_id))

        # Reset attack army counter
        attackers_to_add = get_army(player_id) * get_attribute(player_id, Attributes.ATTACKS_PER_TURN)
        insert_attribute(player_id, Attributes.ATTACK_ELIGIBLE_SOLDIERS, attackers_to_add, turn, turn)

        # Reset priest channeling
        priests = get_attribute(player_id, Attributes.PRIESTS)
        channeling_to_add = (priests * get_attribute(player_id, Attributes.MAXIMUM_PRIEST_CHANNELING))
        insert_attribute(player_id, Attributes.TOTAL_PRIEST_POWER, channeling_to_add, turn, turn)


# ----------------------------------------
# Conversion
# ----------------------------------------
def attempt_conversion(converter_player_id, quantity, person_type, target_player_id=None):
    game_id = player_get_game(converter_player_id)
    if target_player_id is not None and game_id != player_get_game(target_player_id):
        return False, "Target is in a different game; you cannot interact with them"

    if person_type != "neutral" or (target_player_id is None and person_type == "neutral"):
        if person_type == "neutral" or \
           get_player_pantheon(converter_player_id) == NO_PANTHEON or \
           get_player_pantheon(target_player_id) == NO_PANTHEON or \
           get_player_pantheon(converter_player_id) != get_player_pantheon(target_player_id):
            if person_type == "enemy":
                if quantity <= get_attribute(target_player_id, Attributes.FUNCTIONARIES):
                    conversion_rate = get_attribute(converter_player_id, Attributes.ENEMY_CONVERSION_RATE)
                    attempt_cost = get_attribute(converter_player_id, Attributes.ENEMY_CONVERSION_COST)
                else:
                    return False, "Insufficient functionaries"
            elif person_type == "enemy_priest":
                if quantity <= get_attribute(target_player_id, Attributes.PRIESTS):
                    conversion_rate = get_attribute(converter_player_id, Attributes.ENEMY_PRIEST_CONVERSION_RATE)
                    attempt_cost = get_attribute(converter_player_id, Attributes.ENEMY_PRIEST_CONVERSION_COST)
                else:
                    return False, "Insufficient priests"
            elif person_type == "neutral":
                conversion_rate = get_attribute(converter_player_id, Attributes.NEUTRAL_CONVERSION_RATE)
                attempt_cost = get_attribute(converter_player_id, Attributes.NEUTRAL_CONVERSION_COST)
            else:
                return False, "Invalid type"
            if attempt_cost * quantity <= get_power(converter_player_id):
                if attempt_cost * quantity <= get_attribute(converter_player_id, Attributes.TOTAL_PRIEST_POWER):
                    spend_power(converter_player_id, attempt_cost * quantity)
                    spend_channeling_power(converter_player_id, attempt_cost * quantity)
                    converts = calculate_converts(quantity, conversion_rate)

                    turn = current_turn(game_id)
                    with connect() as cursor:
                        if person_type == "enemy_priest":
                            cursor.execute(
                                "INSERT INTO player_attributes ("
                                "    player_id, attribute_id, value, start_turn, expiry_turn)"
                                "VALUES (?,?,?,?,?)",
                                (target_player_id, Attributes.PRIESTS, -converts, turn, NEVER_EXPIRES))
                        elif person_type == "enemy":
                            cursor.execute(
                                "INSERT INTO player_attributes ("
                                "    player_id, attribute_id, value, start_turn, expiry_turn)"
                                "VALUES (?,?,?,?,?)",
                                (target_player_id, Attributes.FUNCTIONARIES, -converts, turn, NEVER_EXPIRES))
                            cursor.execute(
                                "INSERT INTO player_attributes ("
                                "    player_id, attribute_id, value, start_turn, expiry_turn)"
                                "VALUES (?,?,?,?,?)",
                                (converter_player_id, Attributes.FUNCTIONARIES, converts, turn, NEVER_EXPIRES))
                        elif person_type == "neutral":
                            cursor.execute(
                                "INSERT INTO player_attributes ("
                                "    player_id, attribute_id, value, start_turn, expiry_turn)"
                                "VALUES (?,?,?,?,?)",
                                (converter_player_id, Attributes.FUNCTIONARIES, converts, turn, NEVER_EXPIRES))
                        else:
                            return False, "https://xkcd.com/2200"
                        return True, [converts, attempt_cost * quantity]
                else:
                    return False, "Insufficient priest channeling power."
            else:
                return False, "Insufficient DP."
        else:
            return False, "Cannot convert away from members of the same pantheon."
    else:
        return False, "Do not specify other player when converting neutrals."


def calculate_converts(quantity, chance):
    count = 0
    for i in range(quantity):
        if random.random() <= chance:
            count += 1
    return count


# ----------------------------------------
# Pantheons
# ----------------------------------------
def send_power(source_id, target_id, amount):
    if get_power(source_id) >= amount:
        spend_power(source_id, amount)
        give_power(target_id, amount)
        return True, "Sent."
    else:
        return False, "Insufficient DP."


def create_pantheon(display_name, description):
    name = display_name.casefold()
    with connect() as cursor:
        cursor.execute(
            "INSERT INTO pantheons (name,display_name,description) VALUES (?,?,?)",
            (name, display_name, description))
    return True, get_pantheon_by_name(name)


def join_pantheon(player_id, pantheon_id):
    with connect() as cursor:
        cursor.execute("UPDATE players SET pantheon = ? WHERE id = ?", (pantheon_id, player_id))
    return True, "Successfully added {name} to {pantheon}.".format(name=get_player_info(player_id)[2],
                                                                   pantheon=get_pantheon(pantheon_id)[2])


def leave_pantheon(player_id):
    with connect() as cursor:
        cursor.execute("UPDATE players SET pantheon = -1 WHERE id = ?", (player_id,))
        cursor.execute("INSERT INTO player_attributes (player_id, attribute_id, value) VALUES (?,?,?)", (
            player_id,
            Attributes.ATTACK_ELIGIBLE_SOLDIERS,
            get_attribute(player_id, Attributes.ATTACK_ELIGIBLE_SOLDIERS)))
    return True, "Successfully removed {name} from their pantheon".format(name=get_player_info(player_id)[2])


def player_get_pantheon(player_id):
    with connect() as cursor:
        cursor.execute("SELECT pantheon FROM players WHERE id = ?", (player_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        else:
            return row[0]


def get_pantheon(pantheon_id):
    pantheon = []
    with connect() as cursor:
        cursor.execute("SELECT * FROM pantheons WHERE id = ?", (pantheon_id,))
        for item in cursor.fetchone():
            pantheon.append(item)

    return pantheon


def get_pantheon_by_name(name, game_id):
    pantheon = None
    with connect() as cursor:
        cursor.execute("SELECT * FROM pantheons WHERE name = ? AND game_id = ?", (name, game_id))
        pantheon = cursor.fetchone()[0]
    return pantheon


def get_player_pantheon(player_id):
    pantheon = []
    with connect() as cursor:
        cursor.execute("SELECT pantheon FROM players WHERE id = ?", (player_id,))
        pantheon = cursor.fetchone()[0]
    return pantheon


def get_pantheon_name(pantheon_id):
    name = None
    with connect() as cursor:
        cursor.execute("SELECT display_name FROM pantheons WHERE id = ?", (pantheon_id,))
        row = cursor.fetchone()
        if row is None:
            return "None"
        else:
            return row[0]
    # return name


# ----------------------------------------
# Battles
# ----------------------------------------
def get_buff_cost(player_id, amount):
    casting_cost = 0
    buffed_amount = get_attribute(player_id, Attributes.DP_BUFF_POINTS)
    soldier_count = get_army(player_id)
    buff_cost_multiplier = get_attribute(player_id, Attributes.DP_BUFF_COST_MULTIPLIER)
    for i in range(amount):
        casting_cost += 2 ** (buffed_amount / 10)
        buffed_amount += 1
    casting_cost = int(casting_cost * soldier_count * buff_cost_multiplier)
    print(casting_cost)
    return casting_cost


def cast_buff(source_id, attribute_id, amount, target_id=None):
    # Phase 1: Assertions
    if target_id is None:
        target_id = source_id
    game_id = player_get_game(source_id)
    if player_get_game(target_id) != source_id:
        return False, "Target is in a diffferent game; you cannot interact with them"
    if attribute_id not in {Attributes.ATTACK, Attributes.DEFENSE, Attributes.ARMOR, Attributes.INITIATIVE}:
        return False, "Incorrect attribute. Must be attack, defense, armor, or initiative."
    if not player_id_exists(source_id):
        return False, "User invalid"
    if not player_id_exists(target_id):
        return False, "Target invalid"
    if not attribute_exists(attribute_id):
        return False, "Attribute does not exist."

    # Phase 2: Calculate cost
    casting_cost = get_buff_cost(source_id, amount)
    if get_power(source_id) < casting_cost:
        return False, "Not enough power"

    # Phase 3: Increase cost and spend DP
    turn = current_turn(game_id)
    spend_power(source_id, casting_cost)
    increase_attribute(source_id, Attributes.DP_BUFF_POINTS, amount, turn)
    increase_attribute(target_id, attribute_id, amount, turn)
    return True, "Successfully buffed {name} by {amount}".format(name=get_attribute_name(attribute_id), amount=amount)


def attack(attacker_id, target_id, ordered_army_size):
    if not player_id_exists(attacker_id):
        return None, "Attacker does not exist"
    if not player_id_exists(target_id):
        return None, "Defender does not exist"
    game_id = player_get_game(attacker_id)
    if game_id != player_get_game(target_id):
        return None, "Target is in a different game; you cannot interact with them"

    ordered_army_size = int(ordered_army_size)
    available_attackers = get_attribute(attacker_id, Attributes.ATTACK_ELIGIBLE_SOLDIERS)
    if get_army(target_id) + \
        get_attribute(target_id, Attributes.FUNCTIONARIES) \
            + get_attribute(target_id, Attributes.PRIESTS) > 0:
        if ordered_army_size != 0:
            if ordered_army_size <= available_attackers:
                attackers = ordered_army_size
                attack_value = get_attribute(attacker_id, Attributes.ATTACK)

                attacker_initiative = get_attribute(attacker_id, Attributes.INITIATIVE)
                defender_initiative = get_attribute(attacker_id, Attributes.INITIATIVE)
                defenders = get_army(target_id)
                defense_value = get_attribute(target_id, Attributes.DEFENSE)

                damage_dealt = 0
                damage_received = 0

                first_strike_disabled_attackers = 0
                first_strike_disabled_defenders = 0
                if attacker_initiative > defender_initiative:
                    pre_clash_damage = 0
                    for i in range((attacker_initiative - defender_initiative) // 10):
                        pre_clash_damage += generate_damage(attackers, attack_value)

                    first_strike_count = (attacker_initiative - defender_initiative) / 10
                    first_strike_count -= int(first_strike_count)
                    first_strike_count *= attackers
                    first_strike_count = int(first_strike_count)
                    pre_clash_damage += generate_damage(first_strike_count, attack_value)

                    damage_dealt += deal_attack_damage(target_id, pre_clash_damage)
                    first_strike_disabled_attackers = first_strike_count
                elif attacker_initiative < defender_initiative:
                    pre_clash_damage = 0
                    for i in range((defender_initiative - attacker_initiative) // 10):
                        pre_clash_damage += generate_damage(defenders, defense_value)

                    first_strike_count = (defender_initiative - attacker_initiative) / 10
                    first_strike_count -= int(first_strike_count)
                    first_strike_count *= defenders
                    first_strike_count = int(first_strike_count)
                    pre_clash_damage += generate_damage(first_strike_count, defense_value)

                    damage_received += deal_defense_damage(attacker_id, pre_clash_damage)
                    first_strike_disabled_defenders = first_strike_count

                attack_damage = generate_damage(attackers - first_strike_disabled_attackers, attack_value)
                defense_damage = generate_damage(defenders - first_strike_disabled_defenders, defense_value)

                damage_received += deal_defense_damage(attacker_id, defense_damage)
                damage_dealt += deal_attack_damage(target_id, attack_damage)

                # If some of the attackers die, then they're all ineligible anyway
                # If all of them die, they're all ineligible
                # So we just remove attackers
                attackers_made_ineligible = attackers - damage_received

                # This expires, automatically resetting it at the end of every turn
                turn = current_turn(game_id)
                insert_attribute(
                    attacker_id, Attributes.ATTACK_ELIGIBLE_SOLDIERS, -attackers_made_ineligible, turn, turn)
                return True, [damage_dealt[1], damage_received]
            else:
                return False, "Insufficient attackers available"
        else:
            return False, "Must attack with some units."
    else:
        return False, "The opponent has nothing left to kill!"


def generate_damage(quantity, limit):
    total = 0
    for attack in range(int(quantity)):
        total += random.randint(0, int(limit))
    return total


def expected_damage(player_discord, other_player_discord, quantity):
    return [[0, 0, 0], 0, 0]


def get_army(player_id):
    pantheon = get_player_pantheon(player_id)
    if pantheon == -1:
        return get_attribute(player_id, Attributes.SOLDIERS)
    else:
        soldiers = 0
        players = []
        with connect() as cursor:
            cursor.execute("SELECT id FROM players WHERE pantheon = ?", (pantheon,))
            for item in cursor.fetchall():
                players.append(item[0])
        for player in players:
            soldiers += get_attribute(player, Attributes.SOLDIERS)
        return soldiers


def deal_attack_damage(player_id, damage):
    remaining_damage = damage
    available_defenders = get_army(player_id)
    available_functionaries = get_attribute(player_id, Attributes.FUNCTIONARIES)
    available_priests = get_attribute(player_id, Attributes.PRIESTS)

    defenders_killed = 0
    functionaries_killed = 0
    priests_killed = 0

    if remaining_damage > 0:
        defender_armor = get_attribute(player_id, Attributes.ARMOR)

        # Killed is damage divided by armor
        defenders_killed = int(remaining_damage / defender_armor)

        # Subtract away the damage dealt
        remaining_damage -= available_defenders * defender_armor
        if defenders_killed > 0:
            if defenders_killed > available_defenders:
                defenders_killed = available_defenders
            kill(player_id, defenders_killed, "soldiers")

    if remaining_damage > 0:
        functionary_armor = get_attribute(player_id, Attributes.FUNCTIONARY_ARMOR)
        functionaries_killed = int(remaining_damage / functionary_armor)
        remaining_damage -= available_functionaries * functionary_armor
        if functionaries_killed > 0:
            if functionaries_killed > available_functionaries:
                functionaries_killed = available_functionaries
            kill(player_id, functionaries_killed, "functionaries")

    if remaining_damage > 0:
        priest_armor = get_attribute(player_id, Attributes.FUNCTIONARY_ARMOR)
        priests_killed = int(remaining_damage / priest_armor)
        remaining_damage -= available_priests * priest_armor
        if priests_killed > 0:
            if priests_killed > available_priests:
                priests_killed = available_priests
            kill(player_id, priests_killed, "priests")

    return True, [defenders_killed, functionaries_killed, priests_killed]


def deal_defense_damage(player_id, damage):
    soldiers = get_army(player_id)
    soldiers_killed = 0
    damage = int(damage)
    if soldiers >= damage:
        soldiers_killed = damage
        kill(player_id, damage, "soldiers")
    else:
        soldiers_killed = soldiers
        kill(player_id, soldiers, "soldiers")
    return soldiers_killed


def kill(player_id, quantity, type):
    turn = current_turn(player_get_game(player_id))
    if type == "soldiers":
        insert_attribute(player_id, Attributes.SOLDIERS, -quantity, turn, NEVER_EXPIRES)
    elif type == "functionaries":
        insert_attribute(player_id, Attributes.FUNCTIONARIES, -quantity, turn, NEVER_EXPIRES)
    elif type == "priests":
        insert_attribute(player_id, Attributes.PRIESTS, -quantity, turn, NEVER_EXPIRES)
    elif type == "attackers":
        insert_attribute(player_id, Attributes.ATTACK_ELIGIBLE_SOLDIERS, -quantity, turn, NEVER_EXPIRES)
    else:
        return False, "Incorrect type"
    return True, "Success"


# ------------------------------
# Actions
# ------------------------------
def recruit_soldiers(player_id, quantity):
    # Phase 1: Assertions
    if not player_id_exists(player_id):
        return None
    quantity = int(quantity)

    # Phase 2: Actually changing stuff
    functionary_count = get_attribute(player_id, Attributes.FUNCTIONARIES)
    if functionary_count < quantity:
        return False, "Impossible: not enough functionaries"

    dp_cost = get_attribute(player_id, Attributes.SOLDIER_COST) * quantity
    power = get_power(player_id)

    if power < dp_cost:
        return False, "Impossible: not enough power"

    spend_power(player_id, dp_cost)
    increase_attribute(player_id, Attributes.FUNCTIONARIES, -quantity, NEVER_EXPIRES)
    increase_attribute(player_id, Attributes.SOLDIERS, quantity, NEVER_EXPIRES)
    return True, "Successfully created {soldiers} soldiers.".format(soldiers=quantity)


def disband_soldiers(player_id, quantity):
    # Phase 1: Assertions
    if not player_id_exists(player_id):
        return None
    quantity = int(quantity)

    # Phase 2: Actually changing stuff
    soldier_count = get_attribute(player_id, Attributes.SOLDIERS)
    if soldier_count < quantity:
        return False,  "Impossible: not enough soldiers"

    dp_cost = get_attribute(player_id, Attributes.SOLDIER_DISBAND_COST) * quantity
    power = get_power(player_id)

    if power < dp_cost:
        return False, "Impossible: not enough power"

    spend_power(player_id, dp_cost)
    increase_attribute(player_id, Attributes.SOLDIERS, -quantity, NEVER_EXPIRES)
    increase_attribute(player_id, Attributes.FUNCTIONARIES, quantity, NEVER_EXPIRES)
    return True, "Successfully disbanded {soldiers} soldiers".format(soldiers=quantity)


def recruit_priests(player_id, quantity):
    if not player_id_exists(player_id):
        return False, "User doesn't exist"
    quantity = int(quantity)

    functionary_count = get_attribute(player_id, Attributes.FUNCTIONARIES)
    if functionary_count < quantity:
        return False, "Impossible: not enough functionaries"

    dp_cost = get_attribute(player_id, Attributes.PRIEST_COST) * quantity
    power = get_power(player_id)

    if power < dp_cost:
        return False, "Impossible: not enough power"

    spend_power(player_id, dp_cost)
    increase_attribute(player_id, Attributes.FUNCTIONARIES, -quantity, NEVER_EXPIRES)
    increase_attribute(player_id, Attributes.PRIESTS, quantity, NEVER_EXPIRES)

    new_channeling_power = get_attribute(player_id, Attributes.MAXIMUM_PRIEST_CHANNELING)*quantity
    increase_attribute(player_id, Attributes.TOTAL_PRIEST_POWER, new_channeling_power, NEVER_EXPIRES)
    return True, "Successfully added {priests} priests".format(priests=quantity)
