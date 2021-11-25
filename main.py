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

# TODO: Pantheons
# TODO: battle
# TODO: new turn function


# ----------------------------------------
# User management
# ----------------------------------------
def user_name_exists(name):
  with connect() as cursor:
    cursor.execute("SELECT 1 FROM users WHERE name = ?", (name.casefold(),))
    return cursor.fetchone() is not None

def get_user_by_name(name):
  with connect() as cursor:
    cursor.execute("SELECT discord_id FROM users WHERE name = ?", (name.casefold(),))
    row = cursor.fetchone()
    if row is None:
      return None
    else:
      return row[0]

def user_discord_id_exists(discord_id):
  with connect() as cursor:
    cursor.execute("SELECT 1 FROM users WHERE discord_id = ?", (discord_id,))
    return cursor.fetchone() is not None

def new_user(name, discord_id):
  if not user_discord_id_exists(discord_id) and not user_name_exists(name):
    with connect() as cursor:
      cursor.execute('INSERT INTO players (name, display_name,discord_id) VALUES (?,?,?)', (name.casefold(), name, discord_id))
      cursor.execute("SELECT id FROM players WHERE name = ?", (name.casefold(),))
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

def spend_power(discord_id, power):
  player_power = get_power(discord_id)
  if power <= player_power:
    player_id = get_player_id_from_discord_id(discord_id)
    with connect() as cursor:
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
  with connect() as cursor:
    cursor.execute("SELECT id FROM attributes WHERE name = ?", (name.lower(),))
    attribute_id = cursor.fetchone()[0]
  return attribute_id

def get_attribute(discord_id, attribute_id):
  player_id = get_player_id_from_discord_id(discord_id)
  value = None
  turn = current_turn()
  with connect() as cursor:
    cursor.execute(
      "SELECT SUM(value) FROM player_attributes WHERE player_id=? AND attribute_id=? AND (expiry_turn=-1 OR "
      "expiry_turn>?) AND start_turn<=?",
      (player_id, attribute_id, turn, turn))
    value = cursor.fetchone()[0]
  return value


# ----------------------------------------
# Tech
# ----------------------------------------
def tech_name_exists(name):
  with connect() as cursor:
    cursor.execute("SELECT 1 FROM technologies WHERE name = ?", (name.casefold(),))
    return cursor.fetchone() is not None

def tech_exists(id):
  with connect() as cursor:
    cursor.execute("SELECT 1 FROM technologies WHERE id = ?", (id,))
    return cursor.fetchone() is not None

def new_tech(name, description, cost, bonuses=[], chance_multiplier=1):
  # bonuses should be formatted as [[tech_1_id,value1],[tech_2_id,value2]]
  if bonuses is None:
    bonuses = []
  
  if not tech_name_exists(name):
    with connect() as cursor:
      cursor.execute("INSERT INTO technologies (name,display_name,description,cost,chance_multiplier) VALUES (?,?,?,?,?)",
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

def get_tech_id(name):
  tech_id = None
  with connect() as cursor:
    cursor.execute("SELECT id FROM technologies WHERE name = ?", (name.casefold(),))
    tech_id = cursor.fetchone()[0]
  return tech_id

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
  player_id = get_player_id_from_discord_id(discord_id)
  techs = []
  with connect() as cursor:
    cursor.execute("SELECT technology_id FROM player_technologies WHERE player_id = ?", (player_id,))
    techs = list(map(lambda x: x[0], cursor.fetchall()))
  return techs

def player_has_tech(discord_id, tech_id):
  player_id = get_player_id_from_discord_id(discord_id)
  with connect() as cursor:
    cursor.execute("SELECT 1 FROM player_technologies WHERE player_id = ? AND technology_id = ?", (player_id, tech_id))
    return cursor.fetchone() is not None

# ----------------------------------------
# Research
# ----------------------------------------
def attempt_research(discord_id, tech_id, method):
  if not tech_exists(tech_id):
    return False, "technology does not exist"
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
      return False, "Invalid method"

    success_cost = calculate_tech_cost(discord_id, tech_id)
    attempt_cost = attribute_cost * get_research_cost_multiplier(discord_id)

    if get_power(discord_id) >= attempt_cost + success_cost:
      spend_power(discord_id, attempt_cost)

      if random.random() <= attribute_rate:
        complete_research(discord_id, tech_id)
        spend_power(discord_id, success_cost)
        return True, "success"
      else:
        return False, "failed chance"
    else:
      return False, "Insufficient DP"
  else:
    return False, "already researched"


def calculate_tech_cost(discord_id, tech_id):
  base_cost = get_tech_cost(tech_id)
  player_cost_multiplier = get_research_cost_multiplier(discord_id)
  return base_cost * player_cost_multiplier

def player_has_technology(discord_id, technology_id):
  player_id = get_player_id_from_discord_id(discord_id)
  with connect() as cursor:
    cursor.execute("SELECT 1 FROM player_technologies WHERE player_id = ? AND technology_id = ?", (player_id, technology_id))
    return cursor.fetchone() is not None

def complete_research(discord_id, tech_id):
  player_id = get_player_id_from_discord_id(discord_id)
  if not tech_exists(tech_id):
    return False
  if not player_has_technology(discord_id, tech_id):
    with connect() as cursor:
      cursor.execute("INSERT INTO player_technologies (player_id, technology_id) VALUES (?, ?)", (player_id, tech_id))

      # Apply bonuses
      cursor.execute("SELECT attribute_id,value FROM tech_bonuses WHERE tech_id = ?", (tech_id,))
      
      for bonus in cursor.fetchall():
        bonus_pair = list(bonus)

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
  with connect() as cursor:
    cursor.execute("SELECT value SYSTEM system_variables WHERE name = ?", ("turn",))
    turn = cursor.fetchone()[0]
  return turn

def new_turn():
  pass # TODO


# ----------------------------------------
# Conversion
# ----------------------------------------

# TODO DoubleThought
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
      with connect() as cursor:
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
def get_pantheon(discord_id):
  return 1 # TODO


# new_user("casi", 466015764919353346)
complete_research(1, 1)
'''if __name__ == '__main__':
  app.run()'''
