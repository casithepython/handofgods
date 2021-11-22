import sqlite3
import json

connection = sqlite3.connect('HandOfGods.db')
cursor = connection.cursor()

with open('schema.sql') as f:
    connection.executescript(f.read())

attributes = [
    "attack",
    "defense",
    "initiative",
    "armor",
    "research_cost_multiplier",
    "research_rate_bonus",
    "passive_population_growth_rate",
    "income_per_functional",
]
cursor.execute('INSERT INTO users name VALUE ?', )

connection.commit()
connection.close()