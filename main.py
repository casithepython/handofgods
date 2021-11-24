import json
import random
import sqlite3

from flask import Flask, make_response, request, jsonify

app = Flask(__name__)


def connect():
    global connection
    global cursor
    connection = sqlite3.connect("HandOfGods.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()


def disconnect():
    connection.commit()
    connection.close()


# TODO: admin users

# ----------------------------------------
# User management
# ----------------------------------------
def new_user(name, discord_id):
    if discord_id not in get_discord_ids():
        connect()
        cursor.execute('INSERT INTO players (name,discord_id,tech) VALUES (?,?,?)', (name, discord_id, json.dumps([])))
        cursor.execute("SELECT id FROM players WHERE name = ?", (name,))
        player_id = cursor.fetchone()[0]
        defaults = [
            [1, 0],
            [2, 0],
            [3, 0],
            [4, 0],
            [5, 1],
            [6, 0.05],
            [7, 5],
            [8, 0.2],
            [9, 50],
            [10, 0.1],
            [11, 20],
            [12, 0.7],
            [13, 100],
            [14, 0.2],
            [15, 0.13],
            [16, 1],
            [17, 0],
            [18, 0],
            [19, 1],
            [20, 5],
            [21, 0.1],
            [22, 2],
            [23, 0.2],
            [24, 1],
            [25, 0.05],
            [26, 5],
            [27, 0.5],
            [28, 200],
            [29, 10],
            [30, 0],
            [31, 0],
            [32, 0],
            [33, 0],
            [34, 1000],
            [35, 0],
            [36, 0],
            [37, 0],
            [38, 0],
            [39, 0],
            [40, 0],
            [41, 0],
            [42, 0],
            [43, 0]
        ]
        for default in defaults:
            cursor.execute("INSERT INTO player_attributes (player_id,attribute_id,value,expiry_turn) VALUES (?,?,?,?)",
                           (player_id, default[0], default[1], -1))
        disconnect()
        return True
    else:
        return False

def get_player_id(discord_id):
    connect()
    cursor.execute("SELECT id FROM players WHERE discord_id = ?", (discord_id,))
    player_id = cursor.fetchone()[0]
    disconnect()
    return player_id


def get_research_cost_multiplier(player_id):
    return get_attribute(player_id, 5)


def get_discord_ids():
    connect()
    names = [name[0] for name in cursor.execute("SELECT discord_id FROM players")]
    disconnect()
    return names


# ----------------------------------------
# Power
# ----------------------------------------

def get_power(player_id):
    return get_attribute(player_id, 35)


def spend_power(player_id, power):
    player_power = get_power(player_id)
    if power <= player_power:
        connect()
        cursor.execute(
            "INSERT INTO player_attributes (player_id,attribute_id,value,start_turn,expiry_turn) VALUES (?,?,?,?,?)",
            (player_id, 35, -power, -1, -1))
        disconnect()
        return True
    else:
        return False


# ----------------------------------------
# Attributes
# ----------------------------------------
def get_attribute_id(name):
    connect()
    cursor.execute("SELECT id FROM attributes WHERE name = ?", (name,))
    attribute_id = cursor.fetchone()[0]
    disconnect()
    return attribute_id


def get_attribute(player_id, attribute_id):
    connect()
    cursor.execute(
        "SELECT SUM(value) FROM player_attributes WHERE player_id=? AND attribute_id=? AND (expiry_turn=-1 OR "
        "expiry_turn>?) AND start_turn<=?",
        (player_id, attribute_id, current_turn(), current_turn()))
    value = cursor.fetchone()[0]
    disconnect()
    return value


# ----------------------------------------
# Tech
# ----------------------------------------
def new_tech(name, description, cost, bonuses=[], chance_multiplier=1):
    # bonuses should be formatted as [[tech_1_id,value1],[tech_2_id,value2]]
    if bonuses is None:
        bonuses = []
    if name not in get_tech_names():
        connect()
        cursor.execute("INSERT INTO tech (name,description,cost,chance_multiplier) VALUES (?,?,?,?)",
                       (name, description, cost, chance_multiplier))
        cursor.execute("SELECT id FROM tech WHERE name = ?", (name,))
        tech_id = cursor.fetchone()[0]
        for bonus in bonuses:
            cursor.execute("INSERT INTO tech_bonuses (tech_id,attribute_id,value) VALUES (?,?,?)",
                           (tech_id, bonus[0], bonus[1]))
        disconnect()
        return True
    else:
        return False


def add_tech_bonus(tech_id, attribute_id, value):
    connect()
    cursor.execute("SELECT value FROM tech_bonuses WHERE tech_id = ? AND attribute_id = ?", (tech_id, attribute_id))
    possible_value = cursor.fetchone()
    disconnect()
    if possible_value:
        return False, "already has bonus"
    else:
        connect()
        cursor.execute("INSERT INTO tech_bonuses (tech_id, attribute_id, value) values (?,?,?)",
                       (tech_id, attribute_id, value))
        disconnect()
    return True


def update_tech_bonus(tech_id, attribute_id, value):
    connect()
    cursor.execute("SELECT value FROM tech_bonuses WHERE tech_id = ? AND attribute_id = ?", (tech_id, attribute_id))
    possible_value = cursor.fetchone()
    disconnect()
    if possible_value:
        connect()
        cursor.execute("UPDATE tech_bonuses SET value = ? WHERE attribute_id = ? AND tech_id = ?",
                       (value, attribute_id, tech_id))
    else:
        return False, "no existing bonus"


def get_tech_cost(tech_id):
    connect()
    cursor.execute("SELECT cost from tech WHERE id = ?", (tech_id,))
    cost = cursor.fetchone()[0]
    disconnect()
    return cost


def get_tech_names():
    connect()
    names = [name[0] for name in cursor.execute("SELECT name FROM tech")]
    disconnect()
    return names


def get_tech_chance_multiplier(tech_id):
    connect()
    cursor.execute("SELECT chance_multiplier from tech WHERE id = ?", (tech_id,))
    multiplier = cursor.fetchone()[0]
    disconnect()
    return multiplier


def get_player_tech(player_id):
    connect()
    cursor.execute("SELECT tech FROM players WHERE id = ?", (player_id,))
    tech = json.loads(cursor.fetchall()[0][0])  # Pluck out the JSON with indexes and convert to list
    disconnect()
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

        cost = calculate_cost(player_id, tech_id)
        attempt_cost = attribute_cost * get_research_cost_multiplier(player_id)
        if spend_power(player_id, attempt_cost) and get_power(player_id) > cost:
            if random.random() <= attribute_rate:
                complete_research(player_id, tech_id)
                spend_power(player_id, cost)
                return True
            else:
                return False, "failed chance"
        else:
            return False, "Insufficient DP"
    else:
        return False, "already researched"


def calculate_cost(player_id, tech_id):
    base_cost = get_tech_cost(tech_id)
    player_cost_multiplier = get_research_cost_multiplier(player_id)
    return base_cost * player_cost_multiplier


def complete_research(player_id, tech_id):
    connect()
    cursor.execute("SELECT tech FROM players WHERE id = ?", (player_id,))
    tech = json.loads(cursor.fetchall()[0][0])  # Pluck out the JSON with indexes and convert to list
    if tech_id not in tech:
        tech.append(tech_id)
    cursor.execute("UPDATE players SET tech = ? WHERE id = ?", (json.dumps(tech), player_id))
    disconnect()


# Turns
def current_turn():
    connect()
    cursor.execute("select value from system_variables where name = ?", ("turn",))


# new_user("casi", 466015764919353346)
print(add_tech_bonus(1, 1, 1))
'''if __name__ == '__main__':
    app.run()'''
