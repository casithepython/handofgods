import json
import math
import random
import sqlite3

from flask import Flask

app = Flask(__name__)


class Attributes:
    ATTACK = 1
    DEFENSE = 2
    INITIATIVE = 3
    ARMOR = 4
    ARMOUR = 4
    RESEARCH_COST_MULTIPLIER = 5
    DIVINE_INSPIRATION_RATE = 6
    DIVINE_INSPIRATION_COST = 7
    AWAKE_REVELATION_RATE = 8
    AWAKE_REVELATION_COST = 9
    ASLEEP_REVELATION_RATE = 10
    ASLEEP_REVELATION_COST = 11
    DIVINE_AVATAR_RATE = 12
    DIVINE_AVATAR_COST = 13
    PRIEST_RESEARCH_BONUS = 14
    PASSIVE_POPULATION_GROWTH_RATE = 15
    INCOME_PER_FUNCTIONAL = 16
    INCOME_PER_SOLDIER = 17
    INCOME_PER_PRIEST = 18
    BONUS_POWER_PER_FUNCTIONAL = 19
    PRIEST_INCOME_BOOST_CAPACITY = 20
    ENEMY_CONVERSION_RATE = 21
    ENEMY_CONVERSION_COST = 22
    NEUTRAL_CONVERSION_RATE = 23
    NEUTRAL_CONVERSION_COST = 24
    ENEMY_PRIEST_CONVERSION_RATE = 25
    ENEMY_PRIEST_CONVERSION_COST = 26
    PANTHEON_BONUS_MULTIPLIER = 27
    MAXIMUM_PRIEST_CHANNELING = 28
    PRIEST_COST = 29
    SOLDIER_COST = 30
    SOLDIER_DISBAND_COST = 31
    PRIESTS = 32
    SOLDIERS = 33
    FUNCTIONARIES = 34
    POWER = 35
    TOTAL_CONVERTED = 36
    TOTAL_POACHED = 37
    TOTAL_DESTROYED = 38
    TOTAL_LOST = 39
    TOTAL_MASSACRED = 40
    TOTAL_POPULATION_LOST = 41
    TOTAL_SPENT = 42
    TOTAL_INCOME = 43
    BONUS_POWER_PER_SOLDIER = 44
    BONUS_POWER_PER_PRIEST = 45
    ATTACK_ELIGIBLE_SOLDIERS = 46
    ATTACKS_PER_TURN = 47
    FUNCTIONARY_ARMOR = 48
    FUNCTIONARY_DEFENSE = 49
    TOTAL_PRIEST_POWER = 50
    PRIEST_INCOME_BOOST_RATE = 51


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
# User management
# ----------------------------------------
def user_name_exists(name):
    with connect() as cursor:
        cursor.execute("SELECT 1 FROM players WHERE name = ?", (name.casefold(),))
        return cursor.fetchone() is not None


def get_user_by_name(name):
    with connect() as cursor:
        cursor.execute("SELECT discord_id FROM players WHERE name = ?", (name.casefold(),))
        row = cursor.fetchone()
        if row is None:
            return None
        else:
            return row[0]


def user_discord_id_exists(discord_id):
    with connect() as cursor:
        cursor.execute("SELECT 1 FROM players WHERE discord_id = ?", (discord_id,))
        return cursor.fetchone() is not None


def new_user(name, discord_id):
    if not user_discord_id_exists(discord_id) and not user_name_exists(name):
        with connect() as cursor:
            cursor.execute('INSERT INTO players (name, display_name,discord_id) VALUES (?,?,?)',
                           (name.casefold(), name, discord_id))
            cursor.execute("SELECT discord_id FROM players WHERE name = ?", (name.casefold(),))
            discord_id = cursor.fetchone()[0]
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
                Attributes.PRIEST_COST: 0,
                Attributes.SOLDIER_COST: 0,
                Attributes.SOLDIER_DISBAND_COST: 0,
                Attributes.PRIESTS: 0,
                Attributes.SOLDIERS: 0,
                Attributes.FUNCTIONARIES: 1000,
                Attributes.POWER: 0,
                Attributes.TOTAL_CONVERTED: 0,
                Attributes.TOTAL_POACHED: 0,
                Attributes.TOTAL_DESTROYED: 0,
                Attributes.TOTAL_LOST: 0,
                Attributes.TOTAL_MASSACRED: 0,
                Attributes.TOTAL_POPULATION_LOST: 0,
                Attributes.TOTAL_SPENT: 0,
                Attributes.BONUS_POWER_PER_SOLDIER: 0,
                Attributes.BONUS_POWER_PER_PRIEST: 0,
                Attributes.ATTACKS_PER_TURN: 1,
                Attributes.FUNCTIONARY_ARMOR: 0,
                Attributes.FUNCTIONARY_DEFENSE: 0,
                Attributes.ATTACK_ELIGIBLE_SOLDIERS: 0,
                Attributes.TOTAL_PRIEST_POWER: 0,
                Attributes.PRIEST_INCOME_BOOST_RATE: 5
            }
            for attribute_id, value in defaults.items():
                cursor.execute(
                    "INSERT INTO player_attributes (discord_id,attribute_id,value,expiry_turn) VALUES (?,?,?,?)",
                    (discord_id, attribute_id, value, -1))
        return True, "Successfully added user " + name
    else:
        return False, "User or discord id already in system."


def get_player(discord_id):
    info = get_player_info(discord_id)
    return {"id":info[0],
            "name":info[1],
            "display_name":info[2],
            "discord_id":info[3],
            "pantheon":info[4],
            "tech": get_player_techs(discord_id),
            "attributes":get_player_attributes(discord_id)}


def get_player_id(discord_id):
    return get_player_id_from_discord_id(discord_id)


def get_player_attributes(discord_id):
    return [(get_attribute_name(attribute_id), get_attribute(discord_id,attribute_id)) for attribute_id in range(get_num_attributes())]


def get_player_info(discord_id):
    info = []
    with connect() as cursor:
        for value in cursor.fetchone():
            info.append(value)
    return info


def get_discord_ids():
    discord_ids = []
    with connect() as cursor:
        discord_ids = [discord_id[0] for discord_id in cursor.execute("SELECT discord_id FROM players")]
    return discord_ids


def get_player_names():
    names = None
    with connect() as cursor:
        cursor.execute("SELECT name FROM players")
        names = [row[0] for row in cursor.fetchall()]
    return names


def user_is_admin(discord_id):
    return discord_id in {262098148283908099, 466015764919353346}


def get_research_cost_multiplier(discord_id):
    return get_attribute(discord_id, Attributes.RESEARCH_COST_MULTIPLIER)


def get_player_id_from_discord_id(discord_id):
    with connect() as cursor:
        cursor.execute("SELECT id FROM players WHERE discord_id = ?", (discord_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        else:
            return row[0]


# ----------------------------------------
# Power
# ----------------------------------------

def get_power(discord_id):
    return get_attribute(discord_id, Attributes.POWER)


def give_power(discord_id, power):
    with connect() as cursor:
        cursor.execute(
            "INSERT INTO player_attributes (discord_id,attribute_id,value,start_turn,expiry_turn) VALUES (?,?,?,?,?)",
            (discord_id, Attributes.POWER, power, -1, -1))


def spend_power(discord_id, power):
    player_power = get_power(discord_id)
    if power <= player_power:
        with connect() as cursor:
            cursor.execute(
                "INSERT INTO player_attributes (discord_id,attribute_id,value,start_turn,expiry_turn) VALUES (?,?,?,"
                "?,?)",
                (discord_id, Attributes.POWER, -power, -1, -1))
        return True
    else:
        return False


def has_sufficient_channeling_power(discord_id, amount):
    return amount <= get_attribute(discord_id, Attributes.TOTAL_PRIEST_POWER)


def spend_channeling_power(discord_id, amount):
    insert_attribute(discord_id, Attributes.TOTAL_PRIEST_POWER, -1 * amount, -1, -1)


# ----------------------------------------
# Attributes
# ----------------------------------------
def get_attribute_id(name):
    attribute_id = None
    with connect() as cursor:
        cursor.execute("SELECT id FROM attributes WHERE name = ?", (name.lower(),))
        attribute_id = cursor.fetchone()[0]
    return attribute_id


def insert_attribute(discord_id, attribute_id, value, start_turn, expiry_turn):
    with connect() as cursor:
        cursor.execute("INSERT INTO player_attributes (discord_id, attribute_id, value,start_turn,expiry_turn) "
                       "VALUES (?,?,?,?,?)",
                       (discord_id, attribute_id, value, start_turn, expiry_turn))


def get_attribute(discord_id, attribute_id):
    value = None
    turn = current_turn()
    with connect() as cursor:
        cursor.execute(
            "SELECT SUM(value) FROM player_attributes WHERE discord_id=? AND attribute_id=? AND (expiry_turn=-1 OR "
            "expiry_turn >= ?) AND start_turn<=?",
            (discord_id, attribute_id, turn, turn))
        value = cursor.fetchone()[0]
    return value

def get_attribute_name(attribute_id):
    name = None
    with connect() as cursor:
        cursor.execute("SELECT display_name FROM attributes WHERE id = ?",(attribute_id,))
        name = cursor.fetchone()[0]

    return name


def get_num_attributes():
    num = None
    with connect() as cursor:
        cursor.execute("SELECT id FROM attributes")

        num = len(cursor.fetchall())
    return num
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


def new_tech(name, description, cost, bonuses=[], chance_multiplier=1):
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
        return True
    else:
        return False


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


def get_tech_name(tech_id):
    name = None
    with connect() as cursor:
        cursor.execute("SELECT name from technologies WHERE id = ?", (tech_id,))
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


def get_player_techs(discord_id):
    techs = []
    with connect() as cursor:
        cursor.execute("SELECT technology_id FROM player_technologies WHERE discord_id = ?", (discord_id,))
        techs = list(map(lambda x: x[0], cursor.fetchall()))
    return techs


def player_has_tech(discord_id, tech_id):
    with connect() as cursor:
        cursor.execute("SELECT 1 FROM player_technologies WHERE discord_id = ? AND technology_id = ?",
                       (discord_id, tech_id))
        return cursor.fetchone() is not None


def check_prerequisites(discord_id, tech_id):
    required_prerequisites = []
    for prerequisite in get_hard_prerequisites(tech_id):
        if not player_has_tech(discord_id, prerequisite):
            required_prerequisites.append(prerequisite)

    return len(required_prerequisites) == 0, required_prerequisites


# ----------------------------------------
# Research
# ----------------------------------------
def attempt_research(discord_id, tech_id, method, priest=False):
    if not tech_exists(tech_id):
        return False, "This technology does not exist."
    if not player_has_tech(discord_id, tech_id):
        if method == "divine_inspiration":
            attribute_rate = get_attribute(discord_id, Attributes.DIVINE_INSPIRATION_RATE)
            attribute_cost = get_attribute(discord_id, Attributes.DIVINE_INSPIRATION_COST)
        elif method == "awake_revelation":
            attribute_rate = get_attribute(discord_id, Attributes.AWAKE_REVELATION_RATE)
            attribute_cost = get_attribute(discord_id, Attributes.AWAKE_REVELATION_COST)
        elif method == "asleep_revelation":
            attribute_rate = get_attribute(discord_id, Attributes.ASLEEP_REVELATION_RATE)
            attribute_cost = get_attribute(discord_id, Attributes.ASLEEP_REVELATION_COST)
        elif method == "divine_avatar":
            attribute_rate = get_attribute(discord_id, Attributes.DIVINE_AVATAR_RATE)
            attribute_cost = get_attribute(discord_id, Attributes.DIVINE_AVATAR_COST)
        else:
            return False, "Invalid research method."

        success_cost = calculate_tech_cost(discord_id, tech_id)
        attempt_cost = attribute_cost * get_research_cost_multiplier(discord_id)

        priest_used = False
        if priest:
            if has_sufficient_channeling_power(discord_id, attempt_cost + success_cost):
                attribute_rate += get_attribute(discord_id, Attributes.PRIEST_RESEARCH_BONUS)
                priest_used = True

        if get_power(discord_id) >= attempt_cost + success_cost:
            spend_power(discord_id, attempt_cost)
            if priest_used:
                spend_channeling_power(discord_id, attempt_cost)
            if random.random() <= attribute_rate:
                complete_research(discord_id, tech_id)
                spend_power(discord_id, success_cost)
                if priest_used:
                    spend_channeling_power(discord_id, success_cost)
                return True, "Successfully researched " + get_tech_name(tech_id) + "."
            else:
                return False, "Failed research chance, " + str(attempt_cost) + " DP spent."
        else:
            return False, "You do not have enough DP to attempt this research."
    else:
        return False, "You have already researched this technology."


def calculate_tech_cost(discord_id, tech_id):
    base_cost = get_tech_cost(tech_id)
    player_cost_multiplier = get_attribute(discord_id, Attributes.RESEARCH_COST_MULTIPLIER)
    return base_cost * player_cost_multiplier


def player_has_technology(discord_id, technology_id):
    with connect() as cursor:
        cursor.execute("SELECT 1 FROM player_technologies WHERE discord_id = ? AND technology_id = ?",
                       (discord_id, technology_id))
        return cursor.fetchone() is not None


def complete_research(discord_id, tech_id):
    if not tech_exists(tech_id):
        return False
    if not player_has_technology(discord_id, tech_id):
        with connect() as cursor:
            cursor.execute("INSERT INTO player_technologies (discord_id, technology_id) VALUES (?, ?)",
                           (discord_id, tech_id))

            # Apply bonuses
            cursor.execute("SELECT attribute_id,value FROM tech_bonuses WHERE tech_id = ?", (tech_id,))

            for bonus in cursor.fetchall():
                bonus_pair = list(bonus)

                cursor.execute(
                    "INSERT INTO player_attributes (discord_id,attribute_id,value,start_turn,expiry_turn) values ("
                    "?,?,?,?,?)",
                    (discord_id, bonus_pair[0], bonus_pair[1], -1, -1))
            return True
    else:
        return False


# ----------------------------------------
# Turns
# ----------------------------------------
def current_turn():
    turn = None
    with connect() as cursor:
        cursor.execute("SELECT value FROM system_variables WHERE name = ?", ("turn",))
        turn = cursor.fetchone()[0]
    return turn


def calculate_income(discord_id):
    population_bonus_power = get_attribute(discord_id, Attributes.BONUS_POWER_PER_FUNCTIONAL) + get_attribute(
        discord_id, Attributes.BONUS_POWER_PER_SOLDIER) + get_attribute(discord_id,
                                                                        Attributes.BONUS_POWER_PER_PRIEST)
    boost_capacity_priest = get_attribute(discord_id, Attributes.PRIEST_INCOME_BOOST_CAPACITY)
    boost_capacity = get_attribute(discord_id, Attributes.PRIESTS) * boost_capacity_priest
    income_boost = get_attribute(discord_id, Attributes.PRIEST_INCOME_BOOST_RATE) * min(population_bonus_power,
                                                                                        boost_capacity)

    # Base income
    base_income = \
        get_attribute(discord_id, Attributes.FUNCTIONARIES) * get_attribute(discord_id,
                                                                            Attributes.INCOME_PER_FUNCTIONAL) + \
        get_attribute(discord_id, Attributes.SOLDIERS) * get_attribute(discord_id, Attributes.INCOME_PER_SOLDIER) + \
        get_attribute(discord_id, Attributes.PRIESTS) * get_attribute(discord_id, Attributes.INCOME_PER_PRIEST)

    return income_boost+base_income
def new_turn():
    # Increase turn counter
    with connect() as cursor:
        cursor.execute("UPDATE system_variables SET value = ? WHERE name = ?", (current_turn() + 1, "turn"))

    for discord_id in get_discord_ids():
        # Grow population
        insert_attribute(discord_id,
                         Attributes.FUNCTIONARIES,
                         get_attribute(discord_id, Attributes.FUNCTIONARIES) * get_attribute(discord_id,
                                                                                             Attributes.PASSIVE_POPULATION_GROWTH_RATE),
                         -1,
                         -1
                         )

        # Check for and add income
        # Population bonus power
        give_power(discord_id,calculate_income(discord_id))

        # Reset attack army counter
        attackers_to_add = get_attribute(discord_id, Attributes.SOLDIERS) - get_attribute(discord_id,
                                                                                          Attributes.ATTACK_ELIGIBLE_SOLDIERS)
        insert_attribute(discord_id, Attributes.ATTACK_ELIGIBLE_SOLDIERS, attackers_to_add, -1, -1)

        # Reset priest channeling
        priests = get_attribute(discord_id, Attributes.PRIESTS)
        channeling_to_add = (priests * get_attribute(discord_id, Attributes.MAXIMUM_PRIEST_CHANNELING)) \
                            - get_attribute(discord_id, Attributes.TOTAL_PRIEST_POWER)
        insert_attribute(discord_id, Attributes.TOTAL_PRIEST_POWER, channeling_to_add, -1, -1)


# ----------------------------------------
# Conversion
# ----------------------------------------
def attempt_conversion(player_discord, quantity, person_type, other_player_discord=None):
    if person_type != "neutral" or (other_player_discord is None and person_type == "neutral"):
        if person_type == "neutral" or get_pantheon(player_discord) == -1 or get_pantheon(
                other_player_discord) == -1 or get_pantheon(player_discord) != get_pantheon(other_player_discord):
            if person_type == "enemy":
                if quantity <= get_attribute(other_player_discord, Attributes.FUNCTIONARIES):
                    conversion_rate = get_attribute(player_discord, Attributes.ENEMY_CONVERSION_RATE)
                    attempt_cost = get_attribute(player_discord, Attributes.ENEMY_CONVERSION_COST)
                else:
                    return False, "Insufficient functionaries"
            elif person_type == "enemy_priest":
                if quantity <= get_attribute(other_player_discord, Attributes.PRIESTS):
                    conversion_rate = get_attribute(player_discord, Attributes.ENEMY_PRIEST_CONVERSION_RATE)
                    attempt_cost = get_attribute(player_discord, Attributes.ENEMY_PRIEST_CONVERSION_COST)
                else:
                    return False, "Insufficient priests"
            elif person_type == "neutral":
                conversion_rate = get_attribute(player_discord, Attributes.NEUTRAL_CONVERSION_RATE)
                attempt_cost = get_attribute(player_discord, Attributes.NEUTRAL_CONVERSION_COST)
            else:
                return False, "Invalid type"
            if attempt_cost * quantity <= get_power(player_discord):
                if attempt_cost * quantity <= get_attribute(player_discord, Attributes.TOTAL_PRIEST_POWER):
                    spend_power(player_discord, attempt_cost * quantity)
                    spend_channeling_power(player_discord, attempt_cost * quantity)
                    converts = calculate_converts(quantity, conversion_rate)
                    with connect() as cursor:
                        if person_type == "enemy_priest":
                            cursor.execute(
                                "INSERT INTO player_attributes (discord_id, attribute_id, value, start_turn, expiry_turn) VALUES ("
                                "?,?,?,?,?)",
                                (other_player_discord, Attributes.PRIESTS, -1 * converts, -1, -1))
                        elif person_type == "enemy":
                            cursor.execute(
                                "INSERT INTO player_attributes (discord_id, attribute_id, value,start_turn,expiry_turn) VALUES ("
                                "?,?,?,?,?)",
                                (other_player_discord, Attributes.FUNCTIONARIES, -1 * converts, -1, -1))
                            cursor.execute(
                                "INSERT INTO player_attributes (discord_id, attribute_id, value,start_turn,expiry_turn) VALUES ("
                                "?,?,?,?,?)",
                                (player_discord, Attributes.FUNCTIONARIES, converts, -1, -1))
                        elif person_type == "neutral":
                            cursor.execute(
                                "INSERT INTO player_attributes (discord_id, attribute_id, value,start_turn,expiry_turn) VALUES ("
                                "?,?,?,?,?)",
                                (player_discord, Attributes.FUNCTIONARIES, converts, -1, -1))
                        else:
                            return False, "Something went wrong that should never go wrong. Congratulations, you broke my system."
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
# TODO - construct pantheons
# Pantheon mechanics include:
# getting approval from all players
# adding players to pantheons
# Combined military forces
# Conversion immunity DONE
# Bonus sharing
# Can't attack until a turn after you leave a pantheon

def get_pantheon(discord_id):
    pantheon = None
    with connect() as cursor:
        cursor.execute("SELECT pantheon FROM players WHERE discord_id = ?", (discord_id,))
        pantheon = cursor.fetchone()[0]
    return pantheon


def get_pantheon_name(pantheon_id):
    name = None
    with connect() as cursor:
        cursor.execute("SELECT name FROM pantheons WHERE id = ?", (pantheon_id,))
        name = cursor.fetchone()[0]
    return name

# ----------------------------------------
# Battles
# ----------------------------------------

def attack(discord_id, other_player_id, quantity):
    quantity = int(quantity)
    available_attackers = get_attribute(discord_id, Attributes.ATTACK_ELIGIBLE_SOLDIERS)
    if get_attribute(other_player_id, Attributes.SOLDIERS) + get_attribute(other_player_id,
                                                                           Attributes.FUNCTIONARIES) + get_attribute(
        other_player_id, Attributes.PRIESTS) > 0:
        if quantity != 0:
            if quantity <= available_attackers:
                attackers = quantity
                attack_armor = get_attribute(discord_id, Attributes.ARMOR)
                attack_value = get_attribute(discord_id, Attributes.ATTACK)

                defenders = get_attribute(other_player_id, Attributes.SOLDIERS)
                defense_armor = get_attribute(other_player_id, Attributes.ARMOR)
                defense_value = get_attribute(other_player_id, Attributes.DEFENSE)

                attack_damage = generate_damage(attackers, attack_value)
                attackers_loss = math.floor(attack_damage /
                                            attack_armor)
                defense_damage = generate_damage(defenders, defense_value)
                defenders_loss = math.floor(defense_damage /
                                            defense_armor)

                damage_received = deal_defense_damage(discord_id, defense_damage)
                damage_dealt = deal_attack_damage(other_player_id, attack_damage)

                # If some of the attackers die, then they're all ineligible anyway
                # If all of them die, they're all ineligible
                # So we just remove attackers
                attackers_made_ineligible = attackers

                # This won't expire, because we have to hard reset it at the beginning of every turn anyway
                insert_attribute(discord_id, Attributes.ATTACK_ELIGIBLE_SOLDIERS, -1 * attackers_made_ineligible, -1,
                                 -1)
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
        total += random.randint(0, limit)
    return total


def expected_damage(player_discord, other_player_discord, quantity):
    return [[0, 0, 0], 0, 0]


def get_army(discord_id):
    return get_attribute(discord_id,Attributes.SOLDIERS)


def deal_attack_damage(discord_id, damage):
    remaining_damage = damage
    available_defenders = get_attribute(discord_id, Attributes.SOLDIERS)
    available_functionaries = get_attribute(discord_id, Attributes.FUNCTIONARIES)
    available_priests = get_attribute(discord_id, Attributes.PRIESTS)

    defenders_killed = 0
    functionaries_killed = 0
    priests_killed = 0

    if remaining_damage > 0:
        defender_armor = get_attribute(discord_id, Attributes.ARMOR)

        # Killed is damage divided by armor
        defenders_killed = int(remaining_damage / defender_armor)

        # Subtract away the damage dealt
        remaining_damage -= available_defenders * defender_armor
        if defenders_killed > 0:
            if defenders_killed > available_defenders:
                defenders_killed = available_defenders
            kill(discord_id, defenders_killed, "soldiers")

    if remaining_damage > 0:
        functionary_armor = get_attribute(discord_id, Attributes.FUNCTIONARY_ARMOR)
        functionaries_killed = int(remaining_damage / functionary_armor)
        remaining_damage -= available_functionaries * functionary_armor
        if functionaries_killed > 0:
            if functionaries_killed > available_functionaries:
                functionaries_killed = available_functionaries
            kill(discord_id, functionaries_killed, "functionaries")

    if remaining_damage > 0:
        priest_armor = get_attribute(discord_id, Attributes.FUNCTIONARY_ARMOR)
        priests_killed = int(remaining_damage / priest_armor)
        remaining_damage -= available_priests * priest_armor
        if priests_killed > 0:
            if priests_killed > available_priests:
                priests_killed = available_priests
            kill(discord_id, priests_killed, "priests")

    return True, [defenders_killed, functionaries_killed, priests_killed]


def deal_defense_damage(discord_id, damage):
    soldiers = get_attribute(discord_id, Attributes.SOLDIERS)
    soldiers_killed = 0
    damage = int(damage)
    if soldiers >= damage:
        soldiers_killed = damage
        kill(discord_id, damage, "soldiers")
    else:
        soldiers_killed = soldiers
        kill(discord_id, soldiers, "soldiers")
    return soldiers_killed


def kill(discord_id, quantity, type):
    if type == "soldiers":
        insert_attribute(discord_id, Attributes.SOLDIERS, -1 * quantity, -1, -1)
    elif type == "functionaries":
        insert_attribute(discord_id, Attributes.FUNCTIONARIES, -1 * quantity, -1, -1)
    elif type == "priests":
        insert_attribute(discord_id, Attributes.PRIESTS, -1 * quantity, -1, -1)
    elif type == "attackers":
        insert_attribute(discord_id, Attributes.ATTACK_ELIGIBLE_SOLDIERS, -1 * quantity, -1, -1)
    else:
        return False, "Incorrect type"
    return True, "Success"


# new_user("casi", 466015764919353346)
# complete_research(1, 1)
'''if __name__ == '__main__':
  app.run()'''
