import sqlite3
import json

connection = sqlite3.connect('AoPSCoin.db')
cursor = connection.cursor()

with open('schema.sql') as f:
    connection.executescript(f.read())

amountOfCoins = 1000000
coins = []
for i in range(amountOfCoins):
    coins.append(i)

coins = json.dumps(coins)

cursor.execute('INSERT INTO users (name,coins) VALUES (?,?)', ("AoPSCoin Central Bank", coins))

connection.commit()
connection.close()