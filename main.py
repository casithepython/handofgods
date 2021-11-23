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


# User management
@app.route("/create_user", methods=["POST"])
def create_user():  # put application's code here
    req = request.get_json()
    name = req.get('name')
    return make_response(new_user(name), 200)


def new_user(name):
    if name not in get_names():
        connect()
        cursor.execute("INSERT INTO players (name,tech) VALUES (?,?)", (name, json.dumps([])))
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
            [31, 0]
        ]
        for default in defaults:
            cursor.execute("INSERT INTO player_attributes (player_id,attribute_id,value,expiry_turn) VALUES (?,?,?,?)",
                           (player_id, default[0], default[1], -1))
        disconnect()
        return True
    else:
        return False

def get_power(player_id):
    connect()
    cursor.execute("SELECT power FROM players WHERE id = ?",(player_id,))
    power = int(cursor.fetchone()[0])
    disconnect()
    return power

def spend_power(player_id, power):
    player_power = get_power(player_id)
    if power<=player_power:
        connect()
        cursor.execute("UPDATE players SET power = ? WHERE id = ?", (player_power-power,player_id))
        disconnect()
        return True
    else:
        return False

@app.route("/get_users", methods=["GET"])
def get_users():
    return make_response(jsonify(get_names()), 200)


def get_names():
    connect()
    names = [name[0] for name in cursor.execute("SELECT name FROM players")]
    disconnect()
    return names

def get_tech(player_id):
    connect()
    cursor.execute("SELECT tech FROM players WHERE id = ?", (player_id,))
    tech = json.loads(cursor.fetchall()[0][0])  # Pluck out the JSON with indexes and convert to list
    disconnect()
    return tech

@app.route("/get_player_id", methods=["GET"])
def get_player_id():
    return make_response(get_id(request.args.get("name")), 200)


def get_id(name):
    connect()
    cursor.execute("SELECT id FROM players WHERE name = ?", (name,))
    id = cursor.fetchone()[0]
    disconnect()
    return id


# Tech
@app.route("/get_stat_id", methods=["GET"])
def get_stat_id():
    return make_response(get_attribute_id(request.args.get("name")), 200)


def get_attribute_id(name):
    connect()
    cursor.execute("SELECT id FROM attributes WHERE name = ?", (name,))
    id = cursor.fetchone()[0]
    disconnect()
    return id

def get_attribute(player_id, attribute_id):
    connect()
    cursor.execute("SELECT SUM(value) FROM player_attributes WHERE player_id=? AND attribute_id=? AND (expiry_turn=-1 OR expiry_turn>?)", (player_id, attribute_id, current_turn()))
    value = cursor.fetchone()[0]
    disconnect()
    return value

# Research
@app.route("/research", methods=["POST"])
def research():
    req = request.get_json()
    player_id = req.get("player_id")
    tech_id = req.get("tech_id")
    method = req.get("method")
    if attempt_research(player_id, tech_id, method):
        return make_response("Research succeeded.", 200)
    else:
        return make_response("Research failed.", 200)

def calculate_cost(player_id, tech_id, method_cost):
    # TODO: BUILD THIS
    return method_cost

def attempt_research(player_id, tech_id, method):
    if tech_id not in get_tech(player_id):
        if method == "divine_inspiration":
            attribute_rate = get_attribute(player_id,6)
            attribute_cost = get_attribute(player_id,7)
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

        cost = calculate_cost(player_id, tech_id, attribute_cost)
        if spend_power(player_id,cost):
            if random.random() <= attribute_rate:
                complete_research(player_id, tech_id)
                return True
            else:
                return False, "failed chance"
        else:
            return False, "Insufficient DP"
    else:
        return False, "already researched"


def complete_research(player_id, tech_id):
    connect()
    cursor.execute("SELECT tech FROM players WHERE id = ?", (player_id,))
    tech = json.loads(cursor.fetchall()[0][0])  # Pluck out the JSON with indexes and convert to list
    if tech_id not in tech: tech.append(tech_id)
    cursor.execute("UPDATE players SET tech = ? WHERE id = ?", (json.dumps(tech), player_id))
    disconnect()

# Turns
def current_turn():
    return 1

print(attempt_research(1,2,"divine_inspiration"))


'''if __name__ == '__main__':
    app.run()'''
