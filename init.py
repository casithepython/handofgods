import sqlite3
import json

connection = sqlite3.connect('HandOfGods.db')
cursor = connection.cursor()

with open('schema.sql') as f:
    connection.executescript(f.read())

# All multipliers or rates are in decimals
# All costs are in DP
attributes = [
    # Combat
    "attack",
    "defense",
    "initiative",
    "armor",

    # Research
    "research_cost_multiplier",
    "divine_inspiration_rate",
    "divine_inspiration_cost"
    "awake_revelation_rate",
    "awake_revelation_cost",
    "asleep_revelation_rate",
    "asleep_revelation_cost",
    "divine_avatar_rate",
    "divine_avatar_cost",
    "priest_research_bonus",

    # Income
    "passive_population_growth_rate",
    "income_per_functional",
    "income_per_soldier",
    "income_per_priest",
    "bonus_power_per_functional",
    "priest_income_boost_capacity",

    # Conversion
    "enemy_conversion_rate",
    "enemy_conversion_cost",
    "neutral_conversion_rate"
    "neutral_conversion_cost",
    "enemy_priest_conversion_rate",
    "enemy_priest_conversion_cost",

    # Pantheons
    "pantheon_bonus_multiplier"
    
    # Miscellaneous
    "maximum_priest_channeling",
    "priest_cost",
    "soldier_cost",
    "soldier_disband_cost"
]
for attribute in attributes:
    cursor.execute('INSERT INTO attributes (name) VALUES (?)', (attribute,))

connection.commit()
connection.close()