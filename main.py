import json
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

class transaction:
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

# TODO: Pantheons
# TODO: battle
# TODO: new turn function


# ----------------------------------------
# User management
# ----------------------------------------
def new_user(name, discord_id):
    if discord_id not in get_discord_ids() and name not in list(map(lambda a: a.lower(), get_player_names())):
        with transaction() as cursor:
            cursor.execute('INSERT INTO players (name,discord_id,tech) VALUES (?,?,?)', (name, discord_id, json.dumps([])))
            cursor.execute("SELECT id FROM players WHERE name = ?", (name,))
            player_id = cursor.fetchone()[0]
            defaults = {
                Attributes.ATTACK: 0,
                Attributes.DEFENSE: 0,
                Attributes.INITIATIVE: 0,
                Attributes.ARMOR: 0,
                Attributes.ARMOUR: 1,
                Attributes.RESEARCH_COST_MULTIPLIER: 0.05,
                Attributes.DIVINE_INSPIRATION_RATE: 5,
                Attributes.DIVINE_INSPIRATION_COST: 0.2,
                Attributes.AWAKE_REVELATION_RATE: 50,
                Attributes.AWAKE_REVELATION_COST: 0.1,
                Attributes.ASLEEP_REVELATION_RATE: 20,
                Attributes.ASLEEP_REVELATION_COST: 0.7,
                Attributes.DIVINE_AVATAR_RATE: 100,
                Attributes.DIVINE_AVATAR_COST: 0.2,
                Attributes.PRIEST_RESEARCH_BONUS: 0.13,
                Attributes.PASSIVE_POPULATION_GROWTH_RATE: 1,
                Attributes.INCOME_PER_FUNCTIONAL: 0,
                Attributes.INCOME_PER_SOLDIER: 0,
                Attributes.INCOME_PER_PRIEST: 1,
                Attributes.BONUS_POWER_PER_FUNCTIONAL: 5,
                Attributes.PRIEST_INCOME_BOOST_CAPACITY: 0.1,
                Attributes.ENEMY_CONVERSION_RATE: 2,
                Attributes.ENEMY_CONVERSION_COST: 0.2,
                Attributes.NEUTRAL_CONVERSION_RATE: 1,
                Attributes.NEUTRAL_CONVERSION_COST: 0.05,
                Attributes.ENEMY_PRIEST_CONVERSION_RATE: 5,
                Attributes.ENEMY_PRIEST_CONVERSION_COST: 0.5,
                Attributes.PANTHEON_BONUS_MULTIPLIER: 200,
                Attributes.MAXIMUM_PRIEST_CHANNELING: 10,
                Attributes.PRIEST_COST: 0,
                Attributes.SOLDIER_COST: 0,
                Attributes.SOLDIER_DISBAND_COST: 0,
                Attributes.PRIESTS: 0,
                Attributes.SOLDIERS: 1000,
                Attributes.FUNCTIONARIES: 0,
                Attributes.POWER: 0,
                Attributes.TOTAL_CONVERTED: 0,
                Attributes.TOTAL_POACHED: 0,
                Attributes.TOTAL_DESTROYED: 0,
                Attributes.TOTAL_LOST: 0,
                Attributes.TOTAL_MASSACRED: 0,
                Attributes.TOTAL_POPULATION_LOST: 0,
                Attributes.TOTAL_SPENT: 0
            }
            for attribute_id, value in defaults.items:
                cursor.execute("INSERT INTO player_attributes (player_id,attribute_id,value,expiry_turn) VALUES (?,?,?,?)",
                            (player_id, attribute_id, value, -1))
        return True
    else:
        return False


def user_is_admin(discord_id):
    return discord_id in [262098148283908099, 466015764919353346]


def get_discord_id_by_name(name):
    player_id = None
    with transaction() as cursor:
        cursor.execute("SELECT discord_id FROM players WHERE LOWER(name) = ?", (name.casefold(),))
        player_id = cursor.fetchone()[0]
    return player_id


def get_player_id(discord_id):
    player_id = None
    with transaction() as cursor:
        cursor.execute("SELECT id FROM players WHERE discord_id = ?", (discord_id,))
        player_id = cursor.fetchone()[0]
    return player_id


def get_research_cost_multiplier(player_id):
    return get_attribute(player_id, 5)


def get_discord_ids():
    names = []
    with transaction() as cursor:
        names = [name[0] for name in cursor.execute("SELECT discord_id FROM players")]
    return names


def get_player_names():
    names = []
    with transaction() as cursor:
        names = [name[0] for name in cursor.execute("SELECT name FROM players")]
    return names


# ----------------------------------------
# Power
# ----------------------------------------

def get_power(player_id):
    return get_attribute(player_id, Attributes.POWER)


def spend_power(player_id, power):
    player_power = get_power(player_id)
    if power <= player_power:
        with transaction() as cursor:
            cursor.execute(
                "INSERT INTO player_attributes (player_id,attribute_id,value,start_turn,expiry_turn) VALUES (?,?,?,?,?)",
                (player_id, 35, -power, -1, -1))
        return True
    else:
        return False


# ----------------------------------------
# Attributes
# ----------------------------------------
def get_attribute_id(name):
    attribute_id = None
    with transaction() as cursor:
        cursor.execute("SELECT id FROM attributes WHERE LOWER(name) = ?", (name.lower(),))
        attribute_id = cursor.fetchone()[0]
    return attribute_id


def get_attribute(player_id, attribute_id):
    value = None
    with transaction() as cursor:
        cursor.execute(
            "SELECT SUM(value) FROM player_attributes WHERE player_id=? AND attribute_id=? AND (expiry_turn=-1 OR "
            "expiry_turn>?) AND start_turn<=?",
            (player_id, attribute_id, current_turn(), current_turn()))
        value = cursor.fetchone()[0]
    return value


# ----------------------------------------
# Tech
# ----------------------------------------
def new_tech(name, description, cost, bonuses=[], chance_multiplier=1):
    # bonuses should be formatted as [[tech_1_id,value1],[tech_2_id,value2]]
    if bonuses is None:
        bonuses = []
    if name not in list(map(lambda a: a.lower(), get_tech_names())):
        with transaction() as cursor:
            cursor.execute("INSERT INTO tech (name,description,cost,chance_multiplier) VALUES (?,?,?,?)",
                        (name, description, cost, chance_multiplier))
            cursor.execute("SELECT id FROM tech WHERE name = ?", (name,))
            tech_id = cursor.fetchone()[0]
            for bonus in bonuses:
                cursor.execute("INSERT INTO tech_bonuses (tech_id,attribute_id,value) VALUES (?,?,?)",
                            (tech_id, bonus[0], bonus[1]))
        return True
    else:
        return False


def add_tech_bonus(tech_id, attribute_id, value):
    possible_value = None
    with transaction() as cursor:
        cursor.execute("SELECT value FROM tech_bonuses WHERE tech_id = ? AND attribute_id = ?", (tech_id, attribute_id))
        possible_value = cursor.fetchone()
    
    if possible_value:
        return False, "already has bonus"
    else:
        with transaction() as cursor:
            cursor.execute("INSERT INTO tech_bonuses (tech_id, attribute_id, value) values (?,?,?)",
                            (tech_id, attribute_id, value))
    return True


def update_tech_bonus(tech_id, attribute_id, value):
    possible_value = None
    with transaction() as cursor:
        cursor.execute("SELECT value FROM tech_bonuses WHERE tech_id = ? AND attribute_id = ?", (tech_id, attribute_id))
        possible_value = cursor.fetchone()
    if possible_value:
        with transaction() as cursor:
            cursor.execute("UPDATE tech_bonuses SET value = ? WHERE attribute_id = ? AND tech_id = ?",
                        (value, attribute_id, tech_id))
    else:
        return False, "no existing bonus" # TODO Only return value


def get_tech_id(name):
    tech_id = None
    with transaction() as cursor:
        cursor.execute("SELECT id from tech WHERE LOWER(id) = ?", (name.lower(),))
        tech_id = cursor.fetchone()[0]
    return tech_id


def get_tech_cost(tech_id):
    cost = None
    with transaction() as cursor:
        cursor.execute("SELECT cost from tech WHERE id = ?", (tech_id,))
        cost = cursor.fetchone()[0]
    return cost


def get_tech_names():
    names = []
    with transaction() as cursor:
        names = [name[0] for name in cursor.execute("SELECT name FROM tech")]
    return names


def get_tech_chance_multiplier(tech_id):
    multiplier = None
    with transaction() as cursor:
        cursor.execute("SELECT chance_multiplier from tech WHERE id = ?", (tech_id,))
        multiplier = cursor.fetchone()[0]
    return multiplier


def get_player_tech(player_id):
    tech = []
    with transaction() as cursor:
        cursor.execute("SELECT tech FROM players WHERE id = ?", (player_id,))
        tech = json.loads(cursor.fetchall()[0][0])  # Pluck out the JSON with indexes and convert to list
    return tech


# ----------------------------------------
# Research
# ----------------------------------------
def attempt_research(player_id, tech_id, method):
    if tech_id not in get_player_tech(player_id):
        if method == "divine_inspiration":
            attribute_rate = get_attribute(player_id, 6)
            attribute_cost = get_attribute(player_id, 7)
        elif method == "awake_revelation":
            attribute_rate = get_attribute(player_id, 8)
            attribute_cost = get_attribute(player_id, 9)
        elif method == "asleep_revelation":
            attribute_rate = get_attribute(player_id, 10)
            attribute_cost = get_attribute(player_id, 11)
        elif method == "divine_avatar":
            attribute_rate = get_attribute(player_id, 12)
            attribute_cost = get_attribute(player_id, 13)
        else:
            return False, "Invalid method"

        cost = calculate_tech_cost(player_id, tech_id)
        attempt_cost = attribute_cost * get_research_cost_multiplier(player_id)
        if spend_power(player_id, attempt_cost) and get_power(player_id) > cost:
            if random.random() <= attribute_rate:
                complete_research(player_id, tech_id)
                spend_power(player_id, cost)
                return True, "success"
            else:
                return False, "failed chance"
        else:
            return False, "Insufficient DP"
    else:
        return False, "already researched"


def calculate_tech_cost(player_id, tech_id):
    base_cost = get_tech_cost(tech_id)
    player_cost_multiplier = get_research_cost_multiplier(player_id)
    return base_cost * player_cost_multiplier


def complete_research(player_id, tech_id):
    with transaction() as cursor:
        cursor.execute("SELECT tech FROM players WHERE id = ?", (player_id,))
        tech = json.loads(cursor.fetchall()[0][0])  # Pluck out the JSON with indexes and convert to list
        if tech_id not in tech:
            tech.append(tech_id)
            cursor.execute("UPDATE players SET tech = ? WHERE id = ?", (json.dumps(tech), player_id))
            cursor.execute("SELECT attribute_id,value FROM tech_bonuses WHERE tech_id = ?", (tech_id,))
            bonuses = []
            for temp_bonus in list(cursor.fetchall()):
                bonuses.append(list(temp_bonus))

            for bonus_pair in bonuses:
                cursor.execute(
                    "INSERT INTO player_attributes (player_id,attribute_id,value,start_turn,expiry_turn) values ("
                    "?,?,?,?,?)",
                    (player_id, bonus_pair[0], bonus_pair[1], -1, -1))
            return True
        else:
            return False


# ----------------------------------------
# Turns
# ----------------------------------------
def current_turn():
    turn = None
    with transaction() as cursor:
        cursor.execute("select value from system_variables where name = ?", ("turn",))
        turn = cursor.fetchone()[0]
    return turn


def new_turn():
    pass


# ----------------------------------------
# Conversion
# ----------------------------------------
def attempt_conversion(player_id, other_player_id, quantity, person_type):
    if get_pantheon(player_id) is None or get_pantheon(other_player_id) is None or get_pantheon(
            player_id) is not get_pantheon(other_player_id):
        if person_type == "enemy":
            if quantity <= get_attribute(other_player_id, Attributes.FUNCTIONARIES):
                conversion_rate = get_attribute(player_id, Attributes.ENEMY_CONVERSION_RATE)
                attempt_cost = get_attribute(player_id, Attributes.ENEMY_CONVERSION_COST)
            else:
                return False, "Insufficient functionaries"
        elif person_type == "enemy_priest":
            if quantity <= get_attribute(other_player_id, Attributes.PRIESTS):
                conversion_rate = get_attribute(player_id, Attributes.ENEMY_PRIEST_CONVERSION_RATE)
                attempt_cost = get_attribute(player_id, Attributes.ENEMY_PRIEST_CONVERSION_COST)
            else:
                return False, "Insufficient priests"
        elif person_type == "neutral":
            conversion_rate = get_attribute(player_id, Attributes.NEUTRAL_CONVERSION_RATE)
            attempt_cost = get_attribute(player_id, Attributes.NEUTRAL_CONVERSION_COST)
        else:
            return False, "Invalid type"
        if attempt_cost * quantity <= get_power(player_id):
            spend_power(player_id, attempt_cost * quantity)
            converts = calculate_conversion_success(quantity, conversion_rate)
            with transaction() as cursor:
                if person_type == "enemy_priest":
                    cursor.execute(
                        "INSERT INTO player_attributes (player_id, attribute_id, value, start_turn, expiry_turn) VALUES ("
                        "?,?,?,?,?)",
                        (other_player_id, Attributes.PRIESTS, -1 * converts, -1, -1))
                elif person_type == "enemy":
                    cursor.execute(
                        "INSERT INTO player_attributes (player_id, attribute_id, value,start_turn,expiry_turn) VALUES ("
                        "?,?,?,?,?)",
                        (other_player_id, Attributes.FUNCTIONARIES, -1 * converts, -1, -1))
                    cursor.execute(
                        "INSERT INTO player_attributes (player_id, attribute_id, value,start_turn,expiry_turn) VALUES ("
                        "?,?,?,?,?)",
                        (player_id, Attributes.FUNCTIONARIES, converts, -1, -1))
                elif person_type == "neutral":
                    cursor.execute(
                        "INSERT INTO player_attributes (player_id, attribute_id, value,start_turn,expiry_turn) VALUES ("
                        "?,?,?,?,?)",
                        (player_id, Attributes.FUNCTIONARIES, converts, -1, -1))
    else:
        return False, "Same pantheon"


def calculate_conversion_success(quantity, chance):
    count = 0
    for i in range(quantity):
        if random.random() <= chance:
            count += 1
    return count


# ----------------------------------------
# Pantheons
# ----------------------------------------
def get_pantheon(player_id):
    return 1


# new_user("casi", 466015764919353346)
complete_research(1, 1)
'''if __name__ == '__main__':
    app.run()'''
