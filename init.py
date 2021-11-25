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
    "divine_inspiration_cost",
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
    "neutral_conversion_rate",
    "neutral_conversion_cost",
    "enemy_priest_conversion_rate",
    "enemy_priest_conversion_cost",

    # Pantheons
    "pantheon_bonus_multiplier",
    
    # Miscellaneous
    "maximum_priest_channeling",
    "priest_cost",
    "soldier_cost",
    "soldier_disband_cost",

    # Base assets
    "priests",
    "soldiers",
    "functionaries",
    "power",

    # Fun post-game stats to look at and brag about
    "total_converted",
    "total_poached",
    "total_destroyed",
    "total_lost",
    "total_massacred",
    "total_population_lost",
    "total_spent",
    "total_income",

    "bonus_power_per_soldier",
    "bonus_power_per_priest",

    "attack_eligible_soldiers",
    "attacks_per_turn",
    "functionary_armor",
    "functionary_defense",
    "total_priest_power",
    "priest_income_boost_rate"
]
for attribute in attributes:
    cursor.execute('INSERT INTO attributes (name) VALUES (?)', (attribute,))

cursor.execute("INSERT INTO system_variables (name,value) values (?,?)", ("turn", 1))
connection.commit()
connection.close()